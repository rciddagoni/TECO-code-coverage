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

import base64
import os,glob
import re
import argparse
import json
import shutil
import requests
import uuid




class Instrumenter:

    def __init__(self):
        self.CONFIG_PATH=''
        self.INDEX_FILE_PATH=''
        #self.INSTRUMENT_FUNCTION_NAME=''
        self.JS_TO_INSTRUMENT=[] # list of js files (paths) that will be appended with js function name that instruments js code
        self.SERVER_URL=''
        self.START_TEST_SESSION_METHOD=''
        self.END_TEST_SESSION_METHOD=''
        self.JS_TO_INSTRUMENT_LIST_METHOD=''
        self.SET_DETECTED_FILES_API_METHOD=''
        self.GET_INSTRUMENT_FUNCTION_NAME_METHOD=''
        self.GET_TEST_SESSION_STATUS_METHOD=''
        self.SET_CONFIG_VALUES_METHOD=''
        self.SET_FILE_CONTENT_METHOD=''
        self.SET_EXECUTABLE_LINES_COUNT_METHOD=''
        self.SEND_INSTRUMENTATION_STATS_METHOD=''
        self.SET_MODULES_API_METHOD=''
        self.SET_ROUTES_API_METHOD=''
        self.WEB_APP_ROOT=''
        self.JS_TO_INJECT=[] # required javascript libraries that will be injected into the webapp
        self.TEMPLATES_TO_INSTRUMENT=[] # list of html files in the project (paths), that should be instrumented; skip index.html
        self.ROUTES_TO_INSTRUMENT=[]
        self.SOURCE_TO_INSTRUMENT=[]
        self.INJECT_MODE=''
        self.MODULES=[]
        self.SOURCE_ABSOLUTE_PATH=''
        self.INSTRUMENTER_INSTANTIATE_FILE=''
        # SPECIFY REGEX FOR CODE YOU WANT TO APPEND WITH INSTRUMENTATION FUNCTION
        # BY DEFAULT IT FINDS JAVASCRIPT FUNCTION DECLARATIONS:
        self.REGEX_LIST=[
            r'function[\w]*\([\w,\s]*\) \{', 
            r'function [\w]+\([\w,\s]*\) \{', 
            r'function [\w]+ \([\w,\s]*\) \{', 
            r'function [\w]+\([\w,\s]*\)[\n]', 
            r'[\w]+.prototype.[\w]+[\s]*=[\s]*function[\s]*\(\)[\s]*{', 
            r'[\w]+.prototype.[\w]+[\s]*=[\s]*function[\s]*\([\w,\s]*\)[\s]*{',
            r'[\w]+.[\w]+[\s]*=[\s]*function[\s]+\([\w\s,]*\)[\s]*{']



    def prepare_js(self,config_path):
        self.CONFIG_PATH=config_path
        # open config and parse
        with open(self.CONFIG_PATH) as config_file:
            config=json.load(config_file)
            self.INJECT_MODE=config["INJECT_MODE"]
            self.INDEX_FILE_PATH=config["indexPath"]
            self.START_TEST_SESSION_METHOD=config["startSessionAPIMethod"]
            self.END_TEST_SESSION_METHOD=config["endSessionAPIMethod"]
            self.JS_TO_INSTRUMENT_LIST_METHOD=config["getJStoInstrumentAPIMethod"]
            self.GET_INSTRUMENT_FUNCTION_NAME_METHOD=config["getInstrumentFunctionNameAPIMethod"]
            self.SET_DETECTED_FILES_API_METHOD=config["setDetectedFilesAPIMethod"]
            self.SET_CONFIG_VALUES_METHOD=config["setConfigValuesAPIMethod"]
            self.SET_FILE_CONTENT_METHOD=config["setFileContentAPIMethod"]
            self.GET_TEST_SESSION_STATUS_METHOD=config["getTestSessionStatusAPIMethod"]
            self.SEND_INSTRUMENTATION_STATS_METHOD=config["sendInstrumentationStatsAPIMethod"]
            self.SET_EXECUTABLE_LINES_COUNT_METHOD=config["setExecutableLineCountAPIMethod"]
            self.SET_ROUTES_API_METHOD=config["setRoutesAPIMethod"]
            self.SET_MODULES_API_METHOD=config["setModulesAPIMethod"]
            self.SERVER_URL=config["instrumentServerURL"]
            self.WEB_APP_ROOT=config["web_app_root"]
            self.SOURCE_ABSOLUTE_PATH=config["SOURCE_ABSOLUTE_PATH"]
            for  md in config["MODULES"]:
                self.MODULES.append(md)
            self.INSTRUMENTER_INSTANTIATE_FILE=config["INSTRUMENTER_INSTANTIATE_FILE"]
            for jsti in config["JS_TO_INSTRUMENT"]:
                self.JS_TO_INSTRUMENT.append(jsti)
            for tinj in config["JS_TO_INJECT"]:
                self.JS_TO_INJECT.append(tinj)
            for tti in config["TEMPLATES_TO_INSTRUMENT"]:
                self.TEMPLATES_TO_INSTRUMENT.append(tti)
            for rti in config["ROUTES_TO_INSTRUMENT"]:
                self.ROUTES_TO_INSTRUMENT.append(rti)
            for sti in config["SOURCE_TO_INSTRUMENT"]:
                self.SOURCE_TO_INSTRUMENT.append(sti)


        # actions:

        self.inject_required_scripts() # to index.html
        self.insert_instrument_function_into_templates() # to other templates if exist
        self.insert_instrument_function() # to js or source files
        # update list of the files in the project root [js and html only]
        self.update_file_list() # send current file list that is under instrumentation to backend
        self.set_routes() # end routes that are being instrumented
        self.set_modules() # modules that app has and can be visited
        self.count_executable_lines() # count executable line for each instrumented file and send to backend





    def inject_required_scripts(self):
        if self.INJECT_MODE==0:
            self.inject_scripts_mode_0()
        elif self.INJECT_MODE==1:
            self.inject_scripts_mode_1()


    def inject_scripts_mode_0(self):
        """
        create <script></script> in the app's index.html
        and initilize INSTRUMENTER and call InitInstrument() method that is in instrument.js to pass
        some variables from config ,like server url, method names etc.
        :return:
        """
        # prepare script snippet
        script_html="\n"
        # required scripts
        for js in self.JS_TO_INJECT:
            filename=os.path.basename(js)
            shutil.copyfile(js,self.WEB_APP_ROOT+"\\"+filename)
            script_html+='<script type="text/javascript" src="'+filename+'"></script>\n'
        # now init script into index.html body
        script_html+='<script>'
        script_html+='var INSTRUMENTER=new jsInstrument("'+self.SERVER_URL+'","'+self.START_TEST_SESSION_METHOD+'","'+self.END_TEST_SESSION_METHOD+'","'+self.JS_TO_INSTRUMENT_LIST_METHOD+'","'+self.SEND_INSTRUMENTATION_STATS_METHOD+'","'+self.GET_TEST_SESSION_STATUS_METHOD+'");\n'
        script_html+='INSTRUMENTER.InstrumentCode("'+str(uuid.uuid4())+'","index.html");</script>\n'
        lines=[] # init
        # get content of index html
        with open(self.INDEX_FILE_PATH,'r') as index:
            lines=index.readlines()
            plain_string=''.join(lines)
            #avoid double injection
            if "INSTRUMENTER" in plain_string.decode('utf-8'):
                return
            # put init code at the end of the file
            lines.insert(0,script_html)       
        with open(self.INDEX_FILE_PATH, 'w') as file:
                file.writelines(lines)


    def inject_scripts_mode_1(self):
        """
        add reference to instrument.js in there
        :return:
        """
        # prepare script snippet
        script_html="\n"
        # copy required scripts to DIST path, not source path
        for js in self.JS_TO_INJECT:
            filename=os.path.basename(js)
            script_html+='<script type="text/javascript" src="'+filename+'"></script>\n'
        lines=[] # init
        # get content of index html which is in source and will be compiled with injected required js
        with open(self.INDEX_FILE_PATH,'r') as index:
            lines=index.readlines()
            plain_string=''.join(lines)
            # put init code at the end of the file
            lines.insert(0,script_html)       
        with open(self.INDEX_FILE_PATH, 'w') as file:
                file.writelines(lines)


    def insert_instrument_function_into_templates(self):
        """
        insert instrument script into each html template
        :return:
        """
        script_html="\n"
        for t in self.TEMPLATES_TO_INSTRUMENT:
             # prepare script snippet
             for js in self.JS_TO_INJECT:
                filename=os.path.basename(js)
                script_html+='<script type="text/javascript" src="'+filename+'"></script>\n'
             script_html+='<script>'
             script_html+='var INSTRUMENTER=new jsInstrument("'+self.SERVER_URL+'","'+self.START_TEST_SESSION_METHOD+'","'+self.END_TEST_SESSION_METHOD+'","'+self.JS_TO_INSTRUMENT_LIST_METHOD+'","'+self.SEND_INSTRUMENTATION_STATS_METHOD+'","'+self.GET_TEST_SESSION_STATUS_METHOD+'");\n'
             script_html+='INSTRUMENTER.InstrumentCode("'+str(uuid.uuid4())+'","'+os.path.basename(t)+'");</script>\n'
             lines=[] # init
             # get content of template html
             with open(t,'r') as templ:
                     lines=templ.readlines()
                     plain_string=''.join(lines)
                     if "INSTRUMENTER" in plain_string.decode('utf-8'):
                        return
                     # put instrumentation function at the end of file
                     lines.insert(0,script_html)    
             # save file - if everythig is ok
             with open(t, 'w') as file:
                    file.writelines(lines)



    def update_file_list(self):
        """
        insert all files that we want to instrument to files table in the backend
        :return:
        """
        # set files
        ct=0
        files={}
        for js_file in self.JS_TO_INSTRUMENT:
            files.update({ct:js_file})
            ct+=1
    
        for source_file in self.SOURCE_TO_INSTRUMENT:
            files.update({ct:source_file})
            ct+=1

        for templ in self.TEMPLATES_TO_INSTRUMENT:
            files.update({ct:templ})
            ct+=1

        # send to backend
        url=self.SERVER_URL+"/"+self.SET_DETECTED_FILES_API_METHOD
        r=requests.get(url,params=files)
        print r.text


        # UNCOMMENT THIS IF YOU NEED TO STORE FILE CONTENT, BASE64 ENCODED
        self.send_file_contents(files)




    def send_file_contents(self,files):
        """
        encodes each files' content with base 64 and sends to backend
        """
         # now, read content of each of those files and send to backend as base 64
        file_contents={}
        for k,v in files.iteritems():
            #k: index number
            #v: file path
            with open(v) as f:
                content=f.read()
                b64=base64.b64encode(content)
                file_contents["file_content"]=b64
                file_contents["filename"]=os.path.basename(v)
                # send to backend
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                url=self.SERVER_URL+"/"+self.SET_FILE_CONTENT_METHOD
                r=requests.post(url,data=file_contents,headers=headers)
                print "file content upload status: "+r.text




 



    def set_routes(self):
        ct=0
        routes={}
        for r in self.ROUTES_TO_INSTRUMENT:
            routes.update({ct:r})
            ct+=1
        

        # send to backend
        url=self.SERVER_URL+"/"+self.SET_ROUTES_API_METHOD
        r=requests.get(url,params=routes)
        print r.text


    def set_modules(self):
        ct=0
        modules={}
        for r in self.MODULES:
            modules.update({ct:r})
            ct+=1
        

        # send to backend
        url=self.SERVER_URL+"/"+self.SET_MODULES_API_METHOD
        r=requests.get(url,params=modules)
        print r.text


    def count_executable_lines(self):
        record={}
        executable_count=0
        for js_file in self.JS_TO_INSTRUMENT:
            with open(js_file) as f:
                record={}
                executable_count=0
                content=f.read()
                words=content.split()
                for w in words:
                    if "INSTRUMENTER." in w.decode('utf-8'):
                            executable_count+=1
                record["file"]=os.path.basename(js_file)
                record["count"]=executable_count
                # send request
                url=self.SERVER_URL+"/"+self.SET_EXECUTABLE_LINES_COUNT_METHOD
                r=requests.get(url,params=record)

        for source_file in self.SOURCE_TO_INSTRUMENT:
            with open(source_file) as f:
                record={}
                executable_count=0
                content=f.read()
                words=content.split()
                for w in words:
                    if "INSTRUMENTER." in w.decode('utf-8'):
                            executable_count+=1
                record["file"]=os.path.basename(source_file)
                record["count"]=executable_count
                # send request
                url=self.SERVER_URL+"/"+self.SET_EXECUTABLE_LINES_COUNT_METHOD
                r=requests.get(url,params=record)

        for templ in self.TEMPLATES_TO_INSTRUMENT:
                with open(templ) as f:
                    executable_count=0
                    record={}
                    content=f.read()
                    words=content.split()
                    for w in words:
                        if "INSTRUMENTER." in w.decode('utf-8'):
                            executable_count+=1
                    record["file"]=os.path.basename(templ)
                    record["count"]=executable_count
                    # send request
                    url=self.SERVER_URL+"/"+self.SET_EXECUTABLE_LINES_COUNT_METHOD
                    r=requests.get(url,params=record)




    def insert_instrument_function(self):
        if self.INJECT_MODE==0:
            self.insert_instrument_function_into_js_0()
        elif self.INJECT_MODE==1:
            self.copy_ts_module_to_source_folder()
            self.insert_instrument_function_into_js_1()


    def copy_ts_module_to_source_folder(self):
         if os.path.exists(self.SOURCE_ABSOLUTE_PATH+"//teco_test_coverage"):
            shutil.rmtree(self.SOURCE_ABSOLUTE_PATH+"//teco_test_coverage")
         shutil.copytree("typescript_module//teco_test_coverage", self.SOURCE_ABSOLUTE_PATH+"//teco_test_coverage")



    def insert_instrument_function_into_js_0(self):
        '''
        MODE 0
        INJECT INTO UN-MINIFIED JS FILES
        :return:
        '''
        for js_file in self.JS_TO_INSTRUMENT:
            file_content=""
            executable_count=0
            append_next_line=False
            filename=os.path.basename(js_file)
            with open(js_file,'r') as f:
                    file_content = f.readlines()

                    # insert instrument function into each function() in the js file
                    for l in range(0,len(file_content)):
                        if append_next_line:
                             file_content[l]='{ INSTRUMENTER.InstrumentCode("'+str(uuid.uuid4())+'","'+filename+'");\n'
                             append_next_line=False
                             continue  # go to the next line
                        for reg in self.REGEX_LIST:
                            p=re.compile(reg) 
                            var=p.search(file_content[l])
                            if var is not None:
                                    if '{' in var.string:
                                        # append function with custom instrumentation fn
                                        file_content[l]=var.string+'INSTRUMENTER.InstrumentCode("'+str(uuid.uuid4())+'","'+filename+'");'
                                    else:
                                        # this line probably looks like function test() \n but no { which is in next line...
                                        append_next_line=True
            # add instrument function at the end of js file to cover all code executed outside functions at file load
            file_content.append('\n'+'INSTRUMENTER.InstrumentCode("'+str(uuid.uuid4())+'","'+filename+'");')
            with open(js_file, 'w') as file:
                file.writelines(file_content)


    def insert_instrument_function_into_js_1(self):
        '''
        MODE 1
        INJECT INTO TS SOURCE FILES
        :return:
        '''
        # first, inject .ts code that instantiates global instance of instrumenter object
        with open(self.INSTRUMENTER_INSTANTIATE_FILE,'r') as f0:
            content=f0.readlines()
            content.insert(0,'import {Instrumenter} from "'+self.SOURCE_ABSOLUTE_PATH+'//teco_test_coverage//instrumenter" //TECO \n')
            # now at the bottom
            content.append('export const INSTRUMENTER=new Instrumenter("'+self.SERVER_URL+'","'+self.START_TEST_SESSION_METHOD+'","'+self.END_TEST_SESSION_METHOD+'","'+self.JS_TO_INSTRUMENT_LIST_METHOD+'","'+self.SEND_INSTRUMENTATION_STATS_METHOD+'","'+self.GET_TEST_SESSION_STATUS_METHOD+'"); \n')
        with open(self.INSTRUMENTER_INSTANTIATE_FILE, 'w') as file:
            file.writelines(content)

        # then inject instrument function
        for source_file in self.SOURCE_TO_INSTRUMENT:
            file_content=""
            executable_count=0
            append_next_line=False
            filename=os.path.basename(source_file)
            with open(source_file,'r') as f:
                    file_content = f.readlines()
                    file_content.insert(0,'import {INSTRUMENTER} from "'+self.INSTRUMENTER_INSTANTIATE_FILE+'" //TECO \n')
                    # insert instrument function
                    for l in range(0,len(file_content)):
                        if append_next_line:
                             file_content[l]='INSTRUMENTER.instrument("'+str(uuid.uuid4())+'","'+filename+'"); \n'
                             append_next_line=False
                             continue  # go to the next line
                        for reg in self.REGEX_LIST:
                            p=re.compile(reg) 
                            var=p.search(file_content[l])
                            if var is not None:
                                       if '{' in var.string:
                                           # append function with custom instrumentation fn
                                           file_content[l]=var.string+'INSTRUMENTER.instrument("'+str(uuid.uuid4())+'","'+filename+'"); \n'
                                       else:
                                           # this line probably looks like function test() \n but no { which is in next line...
                                           append_next_line=True
                  

            with open(source_file, 'w') as file:
                file.writelines(file_content)






# STARTS HERE
parser = argparse.ArgumentParser(description='Get test coverage for specified web app. Start this tool,then run your selenium tests and get test coverage.')
parser.add_argument('configPath', metavar='J', type=str, nargs='+',
                   help='Absolute path to config json file. Required')
#parser.add_argument('triggerBuildNumber',metavar='V', type=str,nargs='+',help='build number that triggered this test session')
args=parser.parse_args()


# store config json path
json_path=args.configPath[0]
print "Parsing JSON config: "+json_path


instrumenter=Instrumenter()
instrumenter.prepare_js(json_path)