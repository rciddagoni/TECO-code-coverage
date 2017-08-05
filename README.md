# WHAT IS THIS?
 
This is a code coverage tool that works with end-2-end functional tests like selenium, designed for web apps. It does not matter what language your tests are written in, the tool is rest api based (Flask) so communication happens independently. 
 
I created a tool that suits my needs and maybe it will someone else's too.
I named it TECO (from 2 words: TEst and COverage).
 
 ![alt tag](http://msporna.github.io/public/teco_gif_1.gif.gif)
 
 
 
# FEATURES
- measures code coverage for js,ts and html files (statement coverage)
- live report updating
- compatible with automated and manual tests
- language independent - your tests can be written in anything
- automatically injects instrumentation function into JS by using provided REGEX 
- it injects a typescript module if you are instrumenting typescript source
- works with Angular2 (Typescript)
- web based dashboard for viewing coverage reports, written in flask
- API written in flask so it can be easily integrated with any CI tool
- measures visited routes
- measures modules that were touched by the tests
- and finally measures efficiency of each test (how many code lines were executed by each test)
- reports are archived
- easily extensible
- browser independent
 

# DEMO
<p>I recorded a short demo presenting TECO tool in action:
 <a href="https://youtu.be/xvQJpqtbM0g">TECO coverage tool demo</a></p>



# HOW IT WORKS
TECO contains javascript file called instrument.js that has an instrumentation function. This js file is injected into each javascript/typescript/html file of tested web app specified in config. The instrumentation function sits in executable code and once triggered, it sends info to TECO backend about which line was just executed. By design, it is injected into functions but as injection is based on REGEX you can inject it anywhere you want or simply paste the instrumentation function manually into your source.
 
All of the above happens by running *instrument2* python script which also registers few things to backend such as files that you want to instrument, routes that app has, modules that app has etc.
 
When your web app is bootstrapped, it's time create new test session in TECO dashboard by calling API function or by using 'start new session' button on UI. Test session must be ended manually (via API call or UI button) after all of the tests are executed. 
 
Backend gathers data sent from instrument.js as app code is being triggered by frontend actions performed by the tests. It can be viewed live in the dashboard. InstrumentCode() function sits in executable code lines of your app so everytime you do some action on UI, code underneeth is executed along with the instrumentCode() function of TECO.
 
When tests are over, test session ends and we have a test coverage report to analyze.
 
 ![alt tag](http://msporna.github.io/public/teco_diagram.png)
 
# HOW TO USE IT

### BEFORE YOU START - ONE TIME ONLY:
 
 1. Install the requirements by running pip install -r requirements.txt
 2. Create a new database by running 'create_database.py' script located in /dashboard folder
 
 
 
Next steps depend from type of your web application. TECO supports web projets written in pure javascript and in typescript (like angular2 apps). Setting one differs sligthly from another.
 
### JAVASCRIPT PROJECT

 
- backup your project before start. 
- make sure your javascript is not minified or compressed in any way
- find self.REGEX_LIST in instrument2.py and modify regex collection if you need. Typical regex list for javascript files:
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

- find config.json and update:
```
indexPath*
web_app_root*
JS_TO_INSTRUMENT*
TEMPLATES_TO_INSTRUMENT
ROUTES_TO_INSTRUMENT
MODULES
```
*required
 
- INJECT_MODE should be 0
- start server from /dashboard by running:
```
python instrument_server.py
```
or execute
```
run_api_windows.bat
```
- start instrument2.py and pass config.json path as command line argument
- you should get couple of '200's in the output console before it finishes
- check your project's files, should be appended by instrumentation code already plus instrument.js should be inside your app's root and referenced in index.html
- go to localhost:5000/dashboard to view dashboard
- create new test session by clicking the dashboard button or calling api request:
```
http://localhost:5000/set_test_session_start?test_session_name=firstSession
```
- in your tests, 2 tweaks should be done
A. make 'set_current_test' request in each test's setup code:
```
http://localhost:5000/set_current_test?name=click%on%something%else&test_id=t1-t2-t3-chrome&touched_module=dashboard
```
- params are:
[name] - test name, nvarchar
[test_id] -test id, nvarchar
[touched_module] - module it touches, for example dashboard, nvarchar
- B. in your test teardown, sleep for 3-4 seconds before closing browser to give instrumentCode time to finish sending instrumentation data to backend
- you should see your test session in localhost:5000/dashboard
- click on it to view report; 
- now it's a good time to start your tests
- if test session was not ended, there will be a red bar at the top saying it's live
- you should see instrumentation data changing in real time
- end test session after you are done by calling
```
http://localhost:5000/set_test_session_end
```
- you now have test coverage report
 
 
 
 
### TYPESCRIPT PROJECT

 
- backup your project before start.
- find self.REGEX_LIST in instrument2.py and modify regex collection if you need. Tested regex for typescript files:
```
self.REGEX_LIST=[
            r'[\w]+[\s]*\([\w\s:,]*\)[\s]*{',
            r'[\w]+[\s]*\([\w\s,:?]*\)[\s]*:[\s]*[\w\<\>\[\]]+[\s]*{'
            ]
```

- find config.json and update:
```
indexPath*
web_app_root*
ROUTES_TO_INSTRUMENT
SOURCE_TO_INSTRUMENT*
SOURCE_ABSOLUTE_PATH*
INSTRUMENTER_INSTANTIATE_FILE*
MODULES
```
*required
 
- INJECT_MODE should be 1
- start server from /dashboard by running:
```
python instrument_server.py
```
or execute
```
run_api_windows.bat
```
- start instrument2.py and pass config.json path as command line argument
- you should get couple of '200's in the output console before it finishes
- check your project's files, should be appended by instrumentation code already plus instrument.js should be inside your app's root and referenced in index.html
- compile your .ts code
- copy instrument.js to output folder (dist)
- go to localhost:5000/dashboard to view dashboard
- create new test session by clicking the dashboard button or calling api request:
```
http://localhost:5000/set_test_session_start?test_session_name=firstSession
```
- in your tests, 2 tweaks should be done
A. make 'set_current_test' request in each test's setup code:
```
http://localhost:5000/set_current_test?name=click%on%something%else&test_id=t1-t2-t3-chrome&touched_module=dashboard
```
- parameters are:
[name] - test name, nvarchar
[test_id] -test id, nvarchar
[touched_module] - module it touches, for example dashboard, nvarchar

B. in your test teardown, sleep for 3-4 seconds before closing browser to give instrumentCode time to finish sending instrumentation data to backend

- you should see your test session in localhost:5000/dashboard
- click on it to view report; 
- now it's a good time to start your tests
- if test session was not ended, there will be a red bar at the top saying it's live
- you should see instrumentation data changing in real time
- end test session after you are done by calling
```
http://localhost:5000/set_test_session_end
```
- you now have test coverage report
 
 
 
# COVERAGE REPORT EXPLAINED

![alt tag](http://msporna.github.io/public/Report-Explained.png)

## View executed lines

While on report page you can click on instrumented file and a popup with its content will be shown. Instrumentation function
entries that were executed are highlighted so you can easily see what your test triggered and what still needs to be covered.

![alt tag](http://msporna.github.io/public/FilePreview1.PNG)

# HOW THE INJECTED CODE LOOKS LIKE

**javascript - before**
```
function function1()
{ 
    console.log("f1");
    function3();
}
```
**javascript - after**
```
function function1()
{ INSTRUMENTER.InstrumentCode("e343fded-aadf-414e-9e46-36095817e052","main.js");
    console.log("f1");
    function3();
}
```

**it looks the same in typescript (INSTRUMENTER is instantiated globally).**
 
**index.html - before**
```
<script type="text/javascript" src="jquery.js"></script>
<script type="text/javascript" src="main.js"></script>

<button id="testButton1" onclick="function1()">Button 1</button>
<button id="testButton2" onclick="function2()">Button 2</button>

<p>output</p>:
<p id="output_paragraph"></p>

<a href="about.html">go to about</a>
```
**index.html - after**
```

<script type="text/javascript" src="instrument.js"></script>
<script>var INSTRUMENTER=new jsInstrument("http://localhost:5000","set_test_session_start","set_test_session_end","get_js_to_instrument","send_instrumentation_stats","get_test_session_status");
INSTRUMENTER.InstrumentCode("ac88a69c-0d3c-425e-85e8-41cec65f08f5","index.html");</script>
<script type="text/javascript" src="jquery.js"></script>
<script type="text/javascript" src="main.js"></script>

<button id="testButton1" onclick="function1()">Button 1</button>
<button id="testButton2" onclick="function2()">Button 2</button>

<p>output</p>:
<p id="output_paragraph"></p>

<a href="about.html">go to about</a>
```

 
# CONFIG.JSON ENTRIES EXPLAINED
- **[lines 2-13]** - method names from the API. If API changes those to be updated instead of code
- **[instrumentServerURL]** the dashboard runs on :5000 by default, but if you change it, remember to update this entry
- **[indexPath]** your index.html
- **[web_app_root]** dist folder of your web app, which is served to clients
- **[JS_TO_INJECT]** list of js files that are to be copied and injected into your web app's index.html. Instrument.js is a must
- **[JS_TO_INSTRUMENT]** list of js files where instrumentCode function is injected
- **[TEMPLATES_TOINSTRUMENT]** list of html templates which are being instrumented
- **[ROUTES_TO_INSTRUMENT]** list of routes that can be visited in your website. Instrument tool will determine which ones were visited based on data from js instrumentation function
- **[SOURCE_TO_INSTRUMENT]** source files like typescript - everything that needs to be compiled into js and shaked before use
- **[SOURCE_ABSOLUTE_PATH]** where your source files lie. Fill only if above is filled
- **[INSTRUMENTER_INSTANTIATE_FILE]** a source file where instrumenter module will be instantiated globally. Instantiation code will be appended on the bottom of the file. Fill only if inject mode=1
- **[INJECT_MODE]** currently only 2 modes are here: 0 (js) and 1 (ts)
- **[MODULES]** all modules that your app has. It will be determined what modules were touched by tests and shown in report
 
 
 
 
# EXAMPLE
I prepared a sample website and robot framework tests for it to showcase the test coverage tool (inject mode 0, not a typescript project)
 
see readme.txt inside example_app/instructions
 
 
 

