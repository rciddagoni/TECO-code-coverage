//called by button 1
function function1()
{
    console.log("f1");
    function3();
}

//called by button 2
function function2()
{
    set_output("function 2 output");
}

//called by function1
function function3()
{
    set_output("function 3 output");
}


//called by function2 and function3
function set_output(output)
{
    $("#output_paragraph").text(output);
}