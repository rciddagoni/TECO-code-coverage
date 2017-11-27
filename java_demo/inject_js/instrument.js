/*
 * Copyright (c) 2016 by Michal Sporna and contributors.  See AUTHORS
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
 */


//does not require jquery
//usage:var instrumenter=new jsInstrument(params here);
//method call example: instrumenter.InstrumentCode();
var jsInstrument = function (serverURL_p, setTestSessionStartMethod_p, setTestSessionEndMethod_p, getJSToInstrumentFileListMethod_p, sendInstrumentationStatsMethod_p, askTestSessionStatusMethod_p) {
    //save values for later use
    this.serverURL = serverURL_p;
    this.setTestSessionStartMethod = setTestSessionStartMethod_p;
    this.setTestSessionEndMethod = setTestSessionEndMethod_p;
    this.getJSToInstrumentFileListMethod = getJSToInstrumentFileListMethod_p;
    this.sendInstrumentationStatsMethod = sendInstrumentationStatsMethod_p;
    this.askTestSessionStatusMethod = askTestSessionStatusMethod_p;

   
    this.executed_count = 0;
    this.executed_lines = [];
 


    /*
     * function that sends instrumentation stats to backend
     */
    this.InstrumentCode = function (line_guid, file_p) {

        

        //log only lines that were not executed yet
        if (!this.checkIfLineWasExecuted(line_guid)) {
            this.executed_lines.push({ "file": file_p, "line_guid": line_guid });


            //send to backend
            var request = new XMLHttpRequest();
            request.open('GET', this.serverURL + "/" + this.sendInstrumentationStatsMethod + "?file=" + file_p + "&line_guid_p=" + line_guid + "&route=" + window.location.href, true);
            request.send();


        }





    }

    /*
     * util method
     */
    this.checkIfLineWasExecuted = function (line_guid) {
        for (var i = 0; i < this.executed_lines.length; i++) {
            if (this.executed_lines[i].line_guid == line_guid) {
                return true;
            }


        }

        return false;
    }
}

















