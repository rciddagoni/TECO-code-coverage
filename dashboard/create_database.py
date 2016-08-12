import sqlite3

PATH='instrument.db'

def main():
    conn = sqlite3.connect(PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE sessions(ID INTEGER PRIMARY KEY AUTOINCREMENT,update_time DATETIME,is_over INTEGER,name VARCHAR(160),total_coverage VARCHAR(10))''')
    c.execute('''CREATE TABLE stats(ID INTEGER PRIMARY KEY AUTOINCREMENT,file_id INTEGER, session_id INTEGER, date DATETIME, filename VARCHAR(4000), line INTEGER, name VARCHAR(100), type_id INTEGER, line_guid VARCHAR(1000), test_id VARCHAR(500), test_name VARCHAR(2000))''')
    c.execute('''CREATE TABLE config(ID INTEGER PRIMARY KEY AUTOINCREMENT,name VARCHAR(100), value VARCHAR(200))''')
    c.execute('''CREATE TABLE files(ID INTEGER PRIMARY KEY AUTOINCREMENT,name VARCHAR(100), path VARCHAR(4000), type VARCHAR(20), executable_lines_count INTEGER, should_instrument INTEGER, is_history INTEGER, content BLOB)''')
    c.execute('''CREATE TABLE visited_routes(ID INTEGER PRIMARY KEY AUTOINCREMENT,route_visited VARCHAR(100),session_id INTEGER)''')
    c.execute('''CREATE TABLE routes(ID INTEGER PRIMARY KEY AUTOINCREMENT,route VARCHAR(100))''')
    c.execute('''CREATE TABLE modules(ID INTEGER PRIMARY KEY AUTOINCREMENT,module VARCHAR(100))''')
    c.execute('''CREATE TABLE visited_modules(ID INTEGER PRIMARY KEY AUTOINCREMENT,module_touched VARCHAR(100),session_id INTEGER)''')
    c.execute('''CREATE TABLE sessions_files(session_id INTEGER, file_id INTEGER)''')
    conn.commit()
    conn.close()


    # insert some default config entries
    conn=sqlite3.connect(PATH)
    c=conn.cursor()
    c.execute("INSERT INTO config(name,value) VALUES(?,?)",("SESSION_TIMEOUT",3600))
    c.execute("INSERT INTO config(name,value) VALUES(?,?)",("PORT",5000))
    c.execute("INSERT INTO config(name,value) VALUES(?,?)",("UPDATE_INTERVAL_SECONDS",10))
    c.execute("INSERT INTO config(name,value) VALUES(?,?)",("SERVER_HOST","0.0.0.0"))
    c.execute("INSERT INTO config(name,value) VALUES(?,?)",("VERSION","1.2.1"))
    c.execute("INSERT INTO config(name,value) VALUES(?,?)",("PROJECT_NAME","Samle Project"))

   

    conn.commit()
    conn.close()




if __name__ == '__main__':
    main()
