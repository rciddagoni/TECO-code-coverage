/*
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
*/

declare var jsInstrument: any;
export class Instrumenter {

			js_instrumenter:any;
			
			constructor(serverURL_p:string, setTestSessionStartMethod_p:string, setTestSessionEndMethod_p:string, getJSToInstrumentFileListMethod_p:string,sendInstrumentationStatsMethod_p:string,askTestSessionStatusMethod_p:string)
            {
                //init jsInstrumenter from instrument.js file
				this.js_instrumenter=new jsInstrument(serverURL_p,setTestSessionStartMethod_p,setTestSessionEndMethod_p,getJSToInstrumentFileListMethod_p,sendInstrumentationStatsMethod_p,askTestSessionStatusMethod_p);
				
			}

			instrument(lineGuid:string,filename:string) {

					//call javascript library to send data to backend
					this.js_instrumenter.InstrumentCode(lineGuid,filename);

	}

}

