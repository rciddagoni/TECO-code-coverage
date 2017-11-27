You need: python 2, java 1.8, selenium and all of the requirements listed in repo root/requirements

0. there is so called instrumenter server that serves rest api used to gather usage statistics and generate coverage report
1. go to repository root/dashboard and run: python create_database.py
2. start instrumenter server from repo root/dashboard by running: python instrument_server.py
3. next step, very important one, is to inject instrumenter.js and instrumenting function into web app that is being tested. This javascript function calls
instrumenter rest api whenever it's triggered via some action on UI like for example button click
4. while in java_demo folder, run instrument2.py with config.json as parameter: python instrument2.py config.json
5. config.json specifies web app that needs to be rigged with instrumenting function and so on.
6. next step is to serve demo web app from root/java_demo/example_app - go to that folder and run: python server.py
7. the example_app is a very simple html+javascript website
8. after above is done create new test session in the dashboard (default: localhost:5000/dashboard) by clicking on create button
9. root/java_demo/tests folder contains selenium java project - you can run either Tests.java as junit or TestRunner.java as application


There is a video in this folder called teco_java_demo.flv and it shows all of the above steps.