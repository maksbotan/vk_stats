var selected_jids = [];
$(document).ready(function() {
    $("#datepicker").datepicker({
        firstDay: 1,
        dateFormat: "dd-mm-yy"
    });
    $("input[name=bydate]").bind("change", function(){
        $("#bydate").toggle("blind", {direction: "vertical"});
    });
    $("input[name=byjid]").bind("change", function(){
        $("#byjid").toggle("blind", {direction: "vertical"});
    });
    $.getJSON($SCRIPT_ROOT + '/_get_jids', function(data){
        var jids = [];
        $.each(data, function(key, value){
            jids.push('<li><a href="#" class="jid" id="' + key + '">' + key + ': ' + value.join(', ') + '</a></li>');
        });

        $('<ul/>', {
            html: jids.join('')
        }).appendTo('#byjid');

        $(".jid").click(function(){
            var jid = $(this).attr("id");
            var index = -1;
            for (i = 0; i < selected_jids.length; i++){
                if (selected_jids[i] == jid)
                    index = i;
            }
            if (index == -1){
                selected_jids.push(jid);
                $(this).css("color", "red");
            } else {
                selected_jids.splice(index, 1);
                $(this).css("color", "blue");
            }
            alert(selected_jids.join('\n'));
        });
    });
    $("#go").click(function(){
        json_request = {};
        if ($("input[name=byjid]").attr("checked")){
            json_request["jids"] = selected_jids;
        }
        if ($("input[name=bydate]").attr("checked")){
            json_request["date"] = $("#datepicker").datepicker("getDate");
        }

        $.post(
            $SCRIPT_ROOT + '/_get_stats',
            { request: JSON.stringify(json_request)},
            function(data){
                $("#stats").text("");
                var tables = [];
                $.each(data.stats, function(index, value){
                    var table = ['<table><th colspan="1">' + value[0] + '</th>'];
                    $.each(value[1], function(index, value){
                        table.push('<tr><td class="left">' + data.jids[value[0]].join(', ') + '</td><td class="right">' + value[1] + '</td></tr>');
                    });
                    table.push('</table><br/>')
                    tables.push(table.join(''));
                });
                $("#stats").html(tables.join(''));
            },
            "json");
    });
});

