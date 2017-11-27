- read main README
- copy config.js to the root folder where instrument2.py is and/or edit paths to the root of web app you want to instrument and also provide index.html path etc. (in config.json)
- start the TECO backend server by executing below inside /dashboard or run run_api_windows.bat
```
python instrument_server.py
```
- find REGEX_LIST in instrument2.py and replace it with below one. Then run instrument2.py and provide config.json path as argument. This REGEX finds javascript functions
```
self.REGEX_LIST=[
            r'function[\w]*\([\w,\s]*\) \{', 
            r'function [\w]+\([\w,\s]*\) \{', 
            r'function [\w]+ \([\w,\s]*\) \{', 
            r'function [\w]+\([\w,\s]*\)[\n]', 
            r'[\w]+.prototype.[\w]+[\s]*=[\s]*function[\s]*\(\)[\s]*{', 
            r'[\w]+.prototype.[\w]+[\s]*=[\s]*function[\s]*\([\w,\s]*\)[\s]*{',
            r'[\w]+.[\w]+[\s]*=[\s]*function[\s]+\([\w\s,]*\)[\s]*{']
```            
- that's it, instrument2.py will inject instrumentation code into the example app
- run 
python server.py
inside example app's folder or run startServer.bat
- visit localhost:8787 to see example app
- go to localhost:5000/dashboard 
- create new test session
- click on that test session to view its details
- now go to example_app/test/selenium and start standalone selenium server by running command line:
```
java -jar selenium-server-standalone.jar -Dwebdriver.chrome.driver=chromedriver.exe
```
or 
```
executing run_selenium_server_standalone.bat
```
- now it's time to execute automated tests and see how they cover the example app
- go to example_app/test and read requirements.txt ->make sure you have those installed (pip install)
- execute tests  by running command inside example_app/test:
```
pybot --loglevel TRACE --variable CUSTOM_LIBRARY:"CustomKeywords.py" -d test_results\ selenium_test.robot
```
or execute:
```
run_tests.bat
```
- tests will start
- go back to localhost:5000/dashboard and report you opened for the new session and you should see test coverage in real time
