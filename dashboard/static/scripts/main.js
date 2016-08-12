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


var timer;
var dashboardTimer;
var coverageChart;
var current_session_total_coverage;

$( document ).ready(function() {
    
   

   //only if this is report.html page:
    if (window.location.href.indexOf("report") > -1) {
        initReportPage();
    }
    else if(window.location.href.indexOf("dashboard") > -1)
    {
        initDashboardPage();

    }
});

function initReportPage()
{
    $("#liveIndicator").toggle(false);
    createBarChartForTotals(total_executed_percent);

    //data tables
    $('#filesCoverageTable').DataTable();
    $('#tcCoverageTable').DataTable();
    $("#routeCoverageTable").DataTable();
    $("#modulesCoverageTable").DataTable();

    //show which lines were executed inside a file when file name is clicked
    $('#filesCoverageTable').on('click', 'td', function () {
        showExecutedLines($(this).closest('tr').find('td:eq(0)').text());
        
    });


    //https://husa.github.io/timer.js/
    timer = new Timer({
        tick: 1,
        ontick: function (sec) {
            updateCoverage();
        },
        onstart: function () {
            console.log('timer started');
        }
    });

    timer.start(19000);
    
}

function initDashboardPage()
{
    $("#testSessionsTable").DataTable({ "bPaginate": false });

    dashboardTimer = new Timer({
        tick: 1,
        ontick: function (sec) {
            updateSessionsList();
        },
        onstart: function () {
            console.log('dashboard timer started');
        }
    });

    dashboardTimer.start(19000);



}

/*
 * called periodically by timer, updates sessions list
 */
function updateSessionsList()
{
    var sessions = [];
    $.ajax({
        url: "/get_sessions",
        type: "get",
        async: true

    }).done(function (data) {
        sessions = data["sessions"];


        //prepare data
        var table = $('#testSessionsTable').DataTable();
        table.clear();
        for (var i = 0; i < sessions.length; i++) {
            var subset = [];
            subset.push(sessions[i].ID);
            subset.push('<a class="hotlink-paragraph-class" href="/report/'+sessions[i].ID+'">'+sessions[i].name+'</a>');
            subset.push(sessions[i].is_active);
            subset.push(sessions[i].date);
            subset.push(sessions[i].total_coverage +"%");
            //update table
            if (subset[0] != undefined && subset[1] != undefined && subset[2] != undefined && subset[3] != undefined && subset[4] != undefined) {
                table.row.add(subset)
                .draw();
            }

        }


    });

}

/*
 * called by interval timer, obtains new test coverage data from backend
 */
function updateCoverage()
{
    var testCoverage = [];
    var executable = 0;
    var executed = 0;
    var total_coverage_value = 0;
    var session_over = "false";
    var test_efficiency = [];
    var routes_covered = [];
    var modules_covered = [];

    $.ajax({
        url: "/get_current_coverage",
        type: "get",
        async: true,
        data:{
            session_id:CURRENT_SESSION_ID
        }

    }).done(function (data) {
        testCoverage = data["test_coverage"];
        executable = data["executable"]
        executed = data["executed"]
        total_coverage_value = data["total_coverage_value"]
        session_over = data["session_over"]
        test_efficiency = data["tc_coverage_list"]
        routes_covered = data["covered_routes_list"]
        modules_covered=data["covered_modules_list"]

        showFilesCoverage(testCoverage, executable, executed, total_coverage_value, session_over,test_efficiency,routes_covered,modules_covered);

    });

    



    
}


function createPieChartForTotals(executed,executable)
{
    //not used anymore but left for reference

    //docs:http://www.chartjs.org/docs/#doughnut-pie-chart-example-usage
    var ctx = $("#pieChart");
    var data = {
        labels: ["executed", "executable"], datasets: [
            {
                data: [executed,executable],
                backgroundColor: [
                    "#2980B9",
                    "#2C3E50"
                ],
                hoverBackgroundColor: ["#F1C40F"]
            }
        ]
    }
    coverageChart = new Chart(ctx, {
        type: 'pie',
        data: data
    });
}


function createBarChartForTotals(total_coverage_value) {
    //docs:http://www.chartjs.org/docs/#bar-chart-example-usage
    var ctx = $("#barChart");
    var data = {
        labels: ["executed"], datasets: [
            {
                label:"coverage",
                data: [total_coverage_value],
                backgroundColor: [
                    "#2980B9",
                    "#2C3E50"
                ],
                hoverBackgroundColor: ["#F1C40F"]
            }
        ]
    }
    coverageChart = new Chart(ctx, {
        type: 'horizontalBar',
        data: data,
        options: {
            scales: {
                xAxes: [{
                    ticks: {
                        beginAtZero: true,
                        min: 0,
                        max:100
                    }
                }]
            }
        }
    });
}

/*
 * refresh UI after obtaining current test coverage stats from backend
 */
function showFilesCoverage(testCoverage, all_executable, all_executed, total_coverage_value,session_over,test_efficiency,routes_covered,modules_covered)
{
   
    if (session_over=="true" || session_over==undefined)
    {
        $("#liveIndicator").toggle(false);
        return;
    }

    //keep showing live indicator
    $("#liveIndicator").toggle(true);
    var table = $('#filesCoverageTable').DataTable();
    table.destroy();

    //prepare data
     var dataSet=[]
     for(var i=0;i<testCoverage.length;i++)
     {
         var subset = [];
         subset.push(testCoverage[i].filename);
         subset.push(testCoverage[i].executable);
         subset.push(testCoverage[i].executed);
         subset.push(testCoverage[i].percent_executed);

         if (subset[0]!=undefined && subset[1]!=undefined && subset[2]!=undefined && subset[3]!=undefined)
         {
             dataSet.push(subset);
         }
         
     }

    $('#filesCoverageTable').DataTable({
        data: dataSet,
        columns: [
            { title: "Name" },
            { title: "Executable Count" },
            { title: 'Execution Count' },
            {title:"Coverage %"}


        ]
    });


    // routes coverage
    var table = $('#routeCoverageTable').DataTable();
    table.destroy();

    //prepare data
    var dataSet = []
    for (var i = 0; i < routes_covered.length; i++) {
        var subset = [];
        subset.push(routes_covered[i].route);
        subset.push(routes_covered[i].visited);


        if (subset[0] != undefined && subset[1] != undefined ) {
            dataSet.push(subset);
        }

    }

    $('#routeCoverageTable').DataTable({
        data: dataSet,
        columns: [
            { title: "Route" },
            { title: "Visited" }


        ]
    });


    // modules coverage
    var table = $('#modulesCoverageTable').DataTable();
    table.destroy();

    //prepare data
    var dataSet = []
    for (var i = 0; i < modules_covered.length; i++) {
        var subset = [];
        subset.push(modules_covered[i].module);
        subset.push(modules_covered[i].visited);


        if (subset[0] != undefined && subset[1] != undefined) {
            dataSet.push(subset);
        }

    }

    $('#modulesCoverageTable').DataTable({
        data: dataSet,
        columns: [
            { title: "Module" },
            { title: "Touched by test" }


        ]
    });

    // test efficiency
    var table = $('#tcCoverageTable').DataTable();
    table.destroy();

    //prepare data
    var dataSet = []
    for (var i = 0; i < test_efficiency.length; i++) {
        var subset = [];
        subset.push(test_efficiency[i].test_id);
        subset.push(test_efficiency[i].total_executed);
        subset.push(test_efficiency[i].coverage);

        if (subset[0] != undefined && subset[1] != undefined && subset[2] != undefined) {
            dataSet.push(subset);
        }

    }

    $('#tcCoverageTable').DataTable({
        data: dataSet,
        columns: [
            { title: "ID" },
            { title: "Execution Count" },
            {title:"Coverage %"}


        ]
    });


    //update pie chart
    coverageChart.data.datasets[0].data[0] = total_coverage_value;
    coverageChart.update();

    current_session_total_coverage = total_coverage_value;

   
   
}


function stopLiveTestSession()
{
    //finish the session in 3 seconds, wait until all of the instrumentation data is collected by backend...
    setInterval(sendStopTestSessionRequest, 3000);

   
}

function sendStopTestSessionRequest()
{
    $.ajax({
        url: "/set_test_session_end",
        type: "get",
        async: false,
        data: {
            test_session_coverage: current_session_total_coverage
        }

    });


    timer.stop();
    $("#liveIndicator").toggle(false);
}

function startTestSession()
{

    var dialog=BootstrapDialog.show({
        title: 'Set name for a new session',
        draggable: true,
        message: 'Name: <input class="new-test-session-name-input" id="testSessionName"></input>',
        
        buttons: [{
            label: 'Start',
            cssClass: 'btn-success',
            action: function (dialog) {
                var name_p = $("#testSessionName").val();
                $.ajax({
                    url: "/set_test_session_start",
                    type: "get",
                    async: true,
                    data: { test_session_name: name_p }
                

                });
                //location.reload();
                dialog.close();
            }
        }, {
            label: 'Cancel',
            cssClass: 'btn-danger',
            action: function (dialog) {
                
                dialog.close();
            }
        }]
    });

    dialog.getModalHeader().css('background-color', '#16A085');


   
}

/*
 * this is to do
 */
function showFiltersPopup()
{
    var dialog = BootstrapDialog.show({
        title: 'Filter test sessions you see',
        draggable: true,
        message: 'THIS IS todo AND DOES NOTHING FOR NOW',

        buttons: [{
            label: 'Apply',
            action: function (dialog) {
                
                dialog.close();
            }
        }, {
            label: 'Cancel',
            action: function (dialog) {

                dialog.close();
            }
        }]
    });

    dialog.getModalHeader().css('background-color', '#2980B9');
}


function backToDashboard()
{
    window.location.href = '/dashboard';
}

function showAbout()
{
    var dialog = BootstrapDialog.show({
        title: 'About',
        draggable: true,
        message: '<p>Tool created by: Michal Sporna</p>',

        buttons: [ {
            label: 'Close',
            action: function (dialog) {

                dialog.close();
            }
        }]
    });

    dialog.getModalHeader().css('background-color', '#1ABC9C');
}

/**
Given a filename, get filecontent and show which lines of the file were executed
**/
function showExecutedLines(filename_p)
{
   

    var fileContent = "";
    var executedLineGuids = [];


    //get file content
    $.ajax({
        url: "/get_file_content",
        type: "get",
        async: false,
        data: {
            filename: filename_p,
            session_id: CURRENT_SESSION_ID
        }

    }).done(function (data) {
        fileContent = data["decoded_content_string"];
        executedLineGuids = data["executed_lines"]
        

    });
    



    //start syntax highlighting
    var modalHtml = '<div id="codeEditor"></div>';
    


    //https://nakupanda.github.io/bootstrap3-dialog/
    var dialog = BootstrapDialog.show({
        title: filename_p + " (highlighted lines were executed)",
        draggable: true,
        message: modalHtml,
        onshown: function (dialogRef) {
            //show code editor, read only, with file content and executed lines highlighted
            var myCodeMirror = CodeMirror(document.getElementById("codeEditor"), {
                value: fileContent,
                mode: "javascript",
                lineNumbers: true,
                readOnly:true
            });

            //now highlight all lines that contain instrumentation function that was executed
            var lineCount = myCodeMirror.lineCount();
            for(var lc=0;lc<lineCount;lc++)
            {
                var lineText = myCodeMirror.getLine(lc);

                for (var i1 = 0; i1 < executedLineGuids.length; i1++) {
                    if (lineText.includes(executedLineGuids[i1], 0)) {
                        //this line contains instrumentation function so highlight it
                        myCodeMirror.markText({ line: lc, ch: 0 }, { line: lc, ch: 10000 }, { css: "background-color:#16A085;" });
                    }
                }

            }
           

           
        },

        buttons: [{
            label: 'Close',
            cssClass: 'btn-warning',
            action: function (dialog) {

                dialog.close();
            }
        }]
    });

    dialog.getModalHeader().css('background-color', '#16A085');
    dialog.getModalDialog().css("width", '90%');
   
}