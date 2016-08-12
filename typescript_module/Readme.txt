HOW TO USE

1. set web_app_root in config and this is where it will copy teco_test_coverage folder to location where your app's source code is 
(source code of your app should be written in typescript in this case)
2. don't forget to also set SOURCE_TO_INSTRUMENT,INSTRUMENTER_INSTANTIATE_FILE in config.json


3. Instrumenter module will be imported and instrumentation function injected into each .ts source file specified in config.json