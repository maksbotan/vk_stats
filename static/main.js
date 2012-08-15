$(function(){
    $("#datepicker").datepicker({
        firstDay: 1,
        dateFormat: "dd-mm-yy"
    });
    //Load range for our calendar
    $.get(
        $SCRIPT_ROOT + '/_get_info',
        {},
        function(data){
            var first_date = new Date(data['first'] * 1000);
            var last_date = new Date(data['last'] * 1000);
            $('#datepicker').datepicker("option", "minDate", first_date);
            $('#datepicker').datepicker("option", "maxDate", last_date);
        });
    $("#go").click(function(){
        date = $('#datepicker').datepicker('getDate');
        month = date.getMonth() + 1;
        if (month < 10)
            month = '0' + month;
        day = date.getDate();
        if (day < 10)
            day = '0' + day;
        request_date = '' + date.getFullYear() + month + day;
        $.get(
            $SCRIPT_ROOT + '/_get_stats',
            { 'date': request_date },
            function(data){
                $('div#stats').empty();
                $('div#error').empty();
                if (data['result'] == 'error'){
                    $('div#error').append('<h1>Error while getting data</h1');
                    $('div#error').append('<p>Error message: ' + data['message'] + '</p>');
                    return;
                }
                table = $('<table id="#stats_table">');
                table.append('<tr><th>Name</th><th>Online time</th></tr>');
                $.each(data['data'], function(index, record){
                    table.append('<tr><td>' + record[0] + '</td><td>' + record[1] + '</td></tr>');
                });
                $('div#stats').append(table);
            },
            "json");
    });
});
