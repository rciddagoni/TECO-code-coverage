'''
Copyright (c) 2016 by Michal Sporna and contributors.  See AUTHORS
for more details.

Some rights reserved.

Redistribution and use in source and binary forms of the software as well
as documentation, with or without modification, are permitted provided
that the following conditions are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.

* The names of the contributors may not be used to endorse or
  promote products derived from this software without specific
  prior written permission.

THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
'''

import datetime
import os
import sqlite3
from flask import render_template, request, Flask, jsonify
from threading import Timer
import base64





CONNECTION_STRING='instrument.db'
CONFIG={} # dict holding key/value of config entries


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


############################# VIEWS #############################################

######################### API ####################################################
@app.route("/")
def hello():
    return 'visit <a href="/dashboard">/dashboard</a> to see dashboard'


@app.route("/set_test_session_start")
def start_test_session():
    session_name=request.args.get("test_session_name")
    make_all_sessions_inactive()
    reset_active_test()
    create_new_test_session(session_name)
    return  "Logged test session start. session name: "+session_name


@app.route("/set_test_session_end")
def stop_test_session():
    session_coverage=request.args.get("test_session_coverage")
    # save test session coverage when it's over
    sql="UPDATE sessions SET total_coverage=:sc WHERE is_over=0"
    params={"sc":str(session_coverage)}
    execute_query(sql,params)
    
    make_all_sessions_inactive()
    return  "Logged test session end."




@app.route("/refresh_config")
def refresh_config():
    get_config()
    return "200"



@app.route("/touch_test_session")
def touch_active_test_session():
    touch_test_session()
    return "200"



@app.route("/set_detected_files", methods = ["GET","POST"])
def set_detected_files():
    data=request.args
    if len(data)>0 and data!=None:
        make_all_files_historical() # all previous files are onlly a reference now
    # now get each value from dict received in post; key is index so do this simple loop:
    for i in data:
        file_path=data[i] #value
        # now save files to db
        sql="INSERT INTO files(name,path,type,executable_lines_count,should_instrument,is_history) VALUES(?,?,?,?,?,?)"
        file, file_extension = os.path.splitext(file_path)
        filename=os.path.basename(file_path)
        # insert
        execute_query(sql,(filename,data[i],file_extension,-1,1,0))
    return "200"


@app.route("/send_instrumentation_stats" , methods = ["GET","POST"])
def send_instrumentation_stats():
    active_session=get_active_test_session()
    file_id=None
    if active_session is not None:
        data=request.args

        save_visited_route(data["route"],active_session[0])

        # I have line number and file name
        sql="SELECT ID FROM files WHERE name= :n AND is_history=0 AND should_instrument=1"
        param={"n":data["file"]}
        conn=sqlite3.connect(CONNECTION_STRING)
        c=conn.cursor()
        c.execute(sql,param)
        file_id=c.fetchone()
        conn.close()
        if file_id is not None:
            # related to test (paired with this stat)
            test_name=get_config_value("CURRENT_TEST_NAME")
            test_id=get_config_value("CURRENT_TEST_ID")
            if test_id==None:
                test_id="null"
            if test_name==None:
                test_name="null"
            sql="INSERT INTO stats(file_id,session_id,date,filename,line_guid,test_id,test_name) VALUES(?,?,?,?,?,?,?)"
            execute_query(sql,(file_id[0],active_session[0],datetime.datetime.now(),data["file"],data["line_guid_p"],test_id,test_name))
            touch_test_session()
    else:
        print "no active test session found"
    return "200"


@app.route("/set_file_content" , methods = ["GET","POST"])
def set_files_content():
    data=request.form
    sql="UPDATE files SET content= :v WHERE name= :n AND is_history=0"
    param={"v":data["file_content"],"n":data["filename"]}
    execute_query(sql,param)
    return "200"


@app.route("/get_file_content")
def get_files_content():
    filename=request.args["filename"]
    session=request.args["session_id"]
    files=get_all_files_for_session(session)
    content=None
    executed_line_guids_list=[]
    for f in files:
        if f[0][1]==filename:
            sql="SELECT content FROM files WHERE ID=:fid"
            param={"fid":f[0][0]}
            conn=sqlite3.connect(CONNECTION_STRING)
            c=conn.cursor()
            c.execute(sql,param)
            content=c.fetchone()
            conn.close()
            # get stats for the file
            stats=get_stats_for_file(f[0][0],session)
            for s in stats:
                executed_line_guids_list.append(s[8])
            break
    decoded_content=base64.b64decode(content[0])
    return jsonify(decoded_content_string=decoded_content,executed_lines=executed_line_guids_list)





@app.route("/set_current_test" , methods = ["GET"])
def set_active_test():
    data=request.args
    current_test=get_config_value("CURRENT_TEST_NAME")
    if current_test==None:
        sql="INSERT INTO config(name,value) VALUES(?,?)"
        param=("CURRENT_TEST_NAME",data["name"])
        execute_query(sql,param)
        sql="INSERT INTO config(name,value) VALUES(?,?)"
        param=("CURRENT_TEST_ID",data["test_id"])
        execute_query(sql,param)
    else:
        sql="UPDATE config SET value= :v WHERE name= :n"
        params={"n":"CURRENT_TEST_NAME","v":data["name"]}
        execute_query(sql,params)
        sql="UPDATE config SET value= :v WHERE name= :n"
        params={"n":"CURRENT_TEST_ID","v":data["test_id"]}
        execute_query(sql,params)
    refresh_config()
    # also save what module is touched by this test
    active_test_session=get_active_test_session()
    if active_test_session==None:
        active_test_session=-1
    else:
        active_test_session=active_test_session[0]
    sql="INSERT INTO visited_modules(module_touched,session_id) VALUES(?,?)"
    params=(data["touched_module"],active_test_session)
    execute_query(sql,params)

    return "200"


@app.route("/reset_current_test" , methods = ["GET"])
def reset_active_test():
    sql='DELETE FROM config WHERE name="CURRENT_TEST_NAME"'
    execute_query(sql)
    sql='DELETE FROM config WHERE name="CURRENT_TEST_ID"'
    execute_query(sql)
    refresh_config()
    return "200"


@app.route("/set_executable_lines_count_for_file" , methods = ["GET","POST"])
def set_executable_lines_count_for_file():
    data=request.args
    sql="UPDATE files SET executable_lines_count= :v WHERE name= :n AND is_history=0"
    param={"v":data["count"],"n":data["file"]}
    execute_query(sql,param)
    return "200"



@app.route("/set_config_values" , methods = ["GET","POST"])
def set_config_values():
    data=request.args
    for a in data:
        param=None
        value=get_config_value(a)
        if value != None:
            sql="UPDATE config SET value= :v WHERE name= :n"
            param={"v":data[a],"n":a}
        else:
            sql="INSERT INTO config(name,value) VALUES(?,?)"
            param=(a,data[a])
        execute_query(sql,param)
    refresh_config()
    return "200"




@app.route("/set_routes", methods = ["GET"])
def set_routes():
    # we are overwriting ,so clear data first
    sql="DELETE FROM routes"
    execute_query(sql)
    # now save data again
    data=request.args
    for a in data:
        sql="INSERT INTO routes(route) VALUES(:r)"
        param={"r":data[a]}
        execute_query(sql,param)

    return "200"


@app.route("/set_modules", methods = ["GET"])
def set_modules():
    # we are overwriting ,so clear data first
    sql="DELETE FROM modules"
    execute_query(sql)
    # now save data again
    data=request.args
    for a in data:
        sql="INSERT INTO modules(module) VALUES(:m)"
        param={"m":data[a]}
        execute_query(sql,param)

    return "200"


@app.route("/get_js_to_instrument")
def get_js_to_instrument():
    files=[]
    sql="SELECT name FROM files WHERE should_instrument=1 AND is_history=0"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    files=c.fetchall()
    conn.close()
    return jsonify(js_to_instrument=files)


@app.route("/get_instrument_function_name")
def get_instrument_function_name():
    return jsonify(instrument_function_name=CONFIG["INSTRUMENT_JS_FUNCTION_NAME"])

@app.route("/get_test_session_status")
def get_test_session_status():
    session_is_active=False
    active_session=get_active_test_session()
    if active_session is not None:
        session_is_active=True
    return jsonify(test_session_status=session_is_active)



@app.route("/version")
def version():
    return str(APP_VERSION)


@app.route("/get_current_coverage")
def get_current_coverage():
    session=request.args["session_id"]
    is_session_over=check_if_session_is_over(session)
    if is_session_over==None or is_session_over[0]==1:
        is_session_over="true"
    else:
        is_session_over="false"
    file={}
    file_details=[]
    all_executable=0
    covered_modules=[]
    all_executed=0
    total_coverage_percent=0
    all_files_to_instrument=get_all_files_to_instrument_for_live_session()

    # loop for each file that was instrumented
    for r in all_files_to_instrument:
        file={}
       
        # now count line executions in this file and session
        executions=0
        executions_result=get_execution_count_for_session(r[0],session)
        if executions_result!=None:
            executions=float(executions_result[0])

        file["filename"]=r[1]
        file["id"]=r[0]
        file["executable"]=r[4]
        file["executed"]=executions
        file["percent_executed"]=(executions/float(r[4])) * 100
        # also, I want a total number of all executable lines across all files
        all_executable+=float(r[4])
        # and total of executed lines across all files
        all_executed+=executions
        file_details.append(file)

    # return total coverage in percent also
    if all_executable>0 and all_executed>0:
            total_coverage_percent=(all_executed/all_executable)*100
    tc_coverage=get_test_cases_coverage(session)
    # append tc coverage with percent coverage value
    for tc_c in tc_coverage:
        percent=float(tc_c["total_executed"])/all_executable
        tc_c["coverage"]=percent*100
    # covered routes
    covered_routes=get_covered_routes(session)
    # covered modules
    covered_modules=get_covered_modules(session)
    return jsonify(covered_modules_list=covered_modules,covered_routes_list=covered_routes,tc_coverage_list=tc_coverage,test_coverage=file_details,executable=all_executable,executed=all_executed,total_coverage_value=total_coverage_percent,session_over=is_session_over)


@app.route("/get_sessions")
def get_sessions():
    session={}
    sessions_list=[]
    # get all test sessions
    sql="SELECT ID, is_over, name, update_time,total_coverage  FROM sessions"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    results=c.fetchall()
    for r in results:
        session={}
        session["ID"]=r[0]
        if r[1]==1:
            session["is_active"]="false"
        else:
            session["is_active"]="true"
        session["name"]=r[2]
        session["date"]=r[3]
        session["total_coverage"]=r[4]
        sessions_list.append(session)
    return jsonify(sessions=sessions_list)


############################## /API ##########################################

###################### TEMPLATES ###############################################

@app.route("/dashboard")
def view_dashboard():
    session={}
    sessions_list=[]
    # get all test sessions
    sql="SELECT ID, is_over, name, update_time,total_coverage FROM sessions"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    results=c.fetchall()
    for r in results:
        session={}
        session["ID"]=r[0]
        if r[1]==1:
            session["is_active"]="false"
        else:
            session["is_active"]="true"
        session["name"]=r[2]
        session["date"]=r[3]
        session["total_coverage"]=r[4]
        sessions_list.append(session)
    # get version
    version=get_config_value("VERSION")
    p_name=get_config_value("PROJECT_NAME")
    return render_template('dashboard.html', sessions=sessions_list,app_version=version,project_name=p_name)


@app.route("/about")
def view_about():
    return render_template('about.html')



@app.route("/report/<session>")
def view_report(session=None):
    file={}
    file_details=[]
    tc_coverage=[]
    covered_routes=[]
    covered_modules=[]
    all_executable=0
    all_executed=0
    total_coverage_percent=0
    all_files_to_instrument=get_all_files_for_session(session)
    # loop for each file that was instrumented
    for r in all_files_to_instrument:
        file={}
        # now count line executions in this file and session
        executions=0
        executions_result=get_execution_count_for_session(r[0][0],session)
        if executions_result!=None:
            executions=float(executions_result[0])

        file["filename"]=r[0][1]
        file["id"]=r[0][0]
        file["executable"]=r[0][4]
        file["executed"]=executions
        try:
            file["percent_executed"]=(executions/float(r[0][4])) * 100
        except:
            return '<p>OOPS!</p><p>EXECUTABLE LINE COUNT FOR FILE CANNOT BE 0 AND IT IS for file: '+file["filename"]+'. REMOVE IT FROM YOUR CONFIG OR SEE WHY THERE IS NO INSTRUMENTATION CODE INSIDE (MAYBE REGEX IS WRONG?)</p>'
        # also, I want a total number of all executable lines across all files
        all_executable+=float(r[0][4])
        # and total of executed lines across all files
        all_executed+=executions
        file_details.append(file)
    
    tc_coverage=get_test_cases_coverage(session)
    # append tc coverage with percent coverage value
    for tc_c in tc_coverage:
        percent=float(tc_c["total_executed"])/all_executable
        tc_c["coverage"]=percent*100
    # covered routes
    covered_routes=get_covered_routes(session)
    # covered modules
    covered_modules=get_covered_modules(session)
    # return total coverage in percent also
    if  all_executable>0 and all_executed>0:
        total_coverage_percent=(all_executed/all_executable)*100

    return render_template('report.html',covered_modules_list=covered_modules,covered_routes_list=covered_routes,tc_coverage_list=tc_coverage,file_details_list=file_details,total_executable=all_executable,total_executed=all_executed,session_id=session,total_coverage_value=total_coverage_percent)
########################### /TEMPLATES ############################################



##########################     CROSS ORIGIN ALLOWANCE    #######################################


@app.after_request
def after_request(response):
  '''
  this server is used as API, so allow cross origin requests
  this function adds headers that allow cross origin to each response
  :param response:
  :return:
  '''
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response


########################## /CROSS ORIGIN ALLOWANCE#######################################



########################## /VIEWS #############################################

#######UTIL############
def execute_query(sql,params=None):
    '''
    generic method used to execute sql query against db
    :param sql:
    :param params:
    :return:
    '''
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    if params!=None:
        c.execute(sql,params)
    else:
        c.execute(sql)
    conn.commit()
    conn.close()


def get_execution_count_for_session(file_id,session_id):
    '''
    each test session has some files that were instrumented
    get unique number of executed lines for specified file in specified session
    (across all tests)
    :param file_id:
    :param session_id:
    :return:
    '''
    sql="SELECT COUNT(DISTINCT line_guid) FROM stats WHERE session_id= :si AND file_id= :f"
    param={"si":session_id, "f":file_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,param)
    executions=c.fetchone()
    conn.close()
    return executions

def get_file_id_by_filename(file_name):
    sql="SELECT ID FROM files WHERE name=:fn AND is_history=0"
    param={"fn":file_name}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,param)
    file_id=c.fetchone()
    conn.close()
    return file_id


def get_stats_for_file(file_id,session_id):
    stats=[]
    sql="SELECT * FROM stats WHERE file_id=:fid AND session_id=:sid"
    param={"fid":file_id,"sid":session_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,param)
    stats=c.fetchall()
    conn.close()
    print "STATS"
    print stats
    return stats


def get_executable_lines_count_for_file(file_id):
    sql="SELECT executable_lines_count,name,ID FROM files where ID= :id"
    param={"id":file_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,param)
    count=c.fetchone()
    conn.close()
    return count

def get_all_files_for_session(session_id):
    results=[]
    sql="SELECT file_id FROM sessions_files WHERE session_id=:sid"
    param={"sid":session_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,param)
    results=c.fetchall()
    conn.close()
    return get_all_files_to_instrument_for_session(results)


def get_file_list_for_live_test_session(session_id):
    # first check if the session is active, if not, do not return anything
    # this is only used for updating results live
    results=None
    sql1="SELECT is_over FROM sessions WHERE ID= :si"
    sql2="SELECT DISTINCT(file_id) FROM stats WHERE session_id= :si"
    param={"si":session_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql1,param)
    is_session_over=c.fetchone()
    if is_session_over[0]==0: #get results for session only if session is active (status:0)
        c.execute(sql2,param)
        results=c.fetchall()
    conn.close()
    return results


def check_if_session_is_over(s_id):
    is_session_over=None
    sql1="SELECT is_over FROM sessions WHERE ID= :si"
    param={"si":s_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql1,param)
    is_session_over=c.fetchone()
    return is_session_over

def get_file_list_for_test_session(session_id):
    sql="SELECT DISTINCT(file_id) FROM stats WHERE session_id= :si"
    param={"si":session_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,param)
    results=c.fetchall()
    conn.close()
    return results


def get_all_files_to_instrument():
    """
    all files that are not history and to be instrumented
    """
    sql="SELECT * FROM files"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    results=c.fetchall()
    conn.close()
    return results


def get_all_files_to_instrument_for_session(file_ids):
    files=[]
    for f in file_ids:
        sql="SELECT * FROM files WHERE ID= :fid"
        param={"fid":f[0]}
        conn=sqlite3.connect(CONNECTION_STRING)
        c=conn.cursor()
        c.execute(sql,param)
        files.append(c.fetchall())
        conn.close()
    return files

def get_all_files_to_instrument_for_live_session():
    """
    all files that are not history and to be instrumented
    """
    sql="SELECT * FROM files WHERE should_instrument=1 AND is_history=0"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    results=c.fetchall()
    conn.close()
    return results

def get_config():
    """
    get config values from database
    :return:
    """
    CONFIG.clear() #clear config
    sql="SELECT * FROM config"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    results=c.fetchall()
    # iterate through the results now...
    for r in results:
        CONFIG[r[1]]=r[2]
    conn.commit()
    conn.close()


def get_config_value(key_p):
    for key,value in CONFIG.iteritems():
        if key==key_p:
            return value
    return None

def touch_test_session():
    '''
    test session expires in x seconds if is not used. Every operation like logging instrument data
    touches test session to keep it active, or user can manually call api from instrument.js and selenium
    execute command to touch it if expects long wait etc.
    :return:
    '''
    now=datetime.datetime.now()
    sql="UPDATE sessions SET update_time= :date WHERE is_over=0"
    sql_param={"date":now}
    execute_query(sql,sql_param)


def get_active_test_session():
    """
    connect to db and get active test session if any
    :return: active session ID or -1 if no active session
    """
    result=None
    sql="SELECT * FROM sessions WHERE is_over=0"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    result=c.fetchone()
    conn.close()
    return result


def save_visited_route(url,session_id):
    '''
    save visited url
    '''
    sql="INSERT INTO visited_routes(route_visited,session_id) VALUES(?,?)"
    execute_query(sql,(url,session_id))




def get_covered_routes(session_id):
    """
    distinct list of route:visited true/false pair for the session
    """
    routes_list=[]
    route_dict={}
    sql="SELECT route FROM routes"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    routes=c.fetchall()
    conn.close()
    if routes!=None:
        for r in routes:
            route_dict={}
            sql="SELECT ID FROM visited_routes WHERE session_id=:sid AND route_visited=:rv"
            params={"sid":session_id,"rv":r[0]}
            conn=sqlite3.connect(CONNECTION_STRING)
            c=conn.cursor()
            c.execute(sql,params)
            route_id=c.fetchone()
            conn.close()
            route_dict["route"]=r[0]
            if route_id!=None:
                # this route was visited
                route_dict["visited"]="true"
            else:
                route_dict["visited"]="false"
            routes_list.append(route_dict)
    return routes_list


def get_covered_modules(session_id):
    '''
    list of app modules touched by tests
    '''
    modules_list=[]
    module_dict={}
    sql="SELECT module FROM modules"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    modules=c.fetchall()
    conn.close()
    if modules!=None:
        for m in modules:
            module_dict={}
            sql="SELECT ID FROM visited_modules WHERE session_id=:sid AND module_touched=:mt"
            params={"sid":session_id,"mt":m[0]}
            conn=sqlite3.connect(CONNECTION_STRING)
            c=conn.cursor()
            c.execute(sql,params)
            module_id=c.fetchone()
            conn.close()
            module_dict["module"]=m[0]
            if module_id!=None:
                module_dict["visited"]="true"
            else:
                module_dict["visited"]="false"
            modules_list.append(module_dict)
    return modules_list


def get_test_cases_coverage(session_id):
    """
    coverage by test case
    """
    tc_stats={}
    tc_stats_list=[]
    total_executed=0
    sql='SELECT DISTINCT(test_id) FROM stats WHERE session_id=:sid AND test_id!="null"'
    params={"sid":session_id}
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql,params)
    tests=c.fetchall()
    conn.close()
    if len(tests)>0:
        for t in tests:
            total_executed=0
            sql="SELECT DISTINCT(file_id) FROM stats WHERE session_id=:sid AND test_id=:tid"
            params={"sid":session_id,"tid":t[0]}
            conn=sqlite3.connect(CONNECTION_STRING)
            c=conn.cursor()
            c.execute(sql,params)
            files=c.fetchall()
            conn.close()
            for f in files:
                line_count=get_executable_lines_count_for_file(f[0])
                # get executions
                sql="SELECT COUNT(DISTINCT line_guid) FROM stats WHERE session_id= :sid AND file_id= :fid AND test_id=:tid"
                params={"sid":session_id,"tid":t[0],"fid":f[0]}
                conn=sqlite3.connect(CONNECTION_STRING)
                c=conn.cursor()
                c.execute(sql,params)
                executed=c.fetchone()
                conn.close()
                total_executed+=executed[0]
            # save test case and it's executions
            tc_stats={}
            tc_stats["test_id"]=t[0]
            tc_stats["total_executed"]=total_executed
            tc_stats["total_executed"]
            
            tc_stats_list.append(tc_stats)
    return tc_stats_list







def make_all_files_historical():
    """
    when refreshed list of project's sources comes in,
    make all previously stored historical.
    We keep them to be able to show historical reports
    :return:
    """
    sql="UPDATE files SET is_history=1"
    execute_query(sql)
    sql="UPDATE files SET should_instrument=0"
    execute_query(sql)


def make_all_sessions_inactive():
    sql="UPDATE sessions SET is_over=1"
    execute_query(sql)



def create_new_test_session(name):
    """
    add test session to db and set it to active
    :return:
    """
    now=datetime.datetime.now()
    is_over=0
    sql="INSERT INTO sessions(update_time,is_over,name,total_coverage) VALUES(?,?,?,?)"
    execute_query(sql,(now,is_over,name,"0"))
    active_session=get_active_test_session()
    active_files=get_active_files()
    for f in active_files:
        sql="INSERT INTO sessions_files VALUES(?,?)"
        execute_query(sql,(active_session[0],f[0]))


def get_active_files():
    sql="SELECT * FROM files WHERE is_history=0"
    conn=sqlite3.connect(CONNECTION_STRING)
    c=conn.cursor()
    c.execute(sql)
    files=c.fetchall()
    conn.close()
    return files




def scheduler_main():
    check_if_test_session_timeout()


def check_if_test_session_timeout():
    active_session_entry=get_active_test_session()
    if active_session_entry is not None:
        start_date=datetime.datetime.strptime(active_session_entry[1], '%Y-%m-%d %H:%M:%S.%f')
        delta=datetime.datetime.now()-start_date
        delta=delta.total_seconds()
        if delta > float(CONFIG["SESSION_TIMEOUT"]):
            make_all_sessions_inactive()
            



################################################## /UTIL #############################################

class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None


################################### BOOTS HERE #####################################################33

if __name__ == "__main__":
    get_config()
    # schedule
    scheduler = Scheduler(float(CONFIG["UPDATE_INTERVAL_SECONDS"]), scheduler_main)
    scheduler.start()
    check_if_test_session_timeout()
    # start the server
    #app.run()
    app.run(host=CONFIG["SERVER_HOST"], port=int(CONFIG["PORT"]),threaded=True)
    scheduler.stop()

