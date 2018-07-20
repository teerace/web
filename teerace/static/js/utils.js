/*
 *      utils.js
 *      Robert Chmielowiec 2011
 */


String.prototype.format = function () {
    var formatted = this;
    for (arg in arguments) {
        formatted = formatted.replace ("{" + arg + "}", arguments[arg]);
    }
    return formatted;
};

Date.prototype.getMonthName = function() {
    var m = ['Jan','Feb','Mar','Apr','May','Jun','Jul', 'Aug','Sep','Oct','Nov','Dec'];
    return m[this.getMonth()];
};

function orly(txt) {
    $('.hide').fadeIn('slow');
    var btn = $('#warn-button');
    $(btn).val(txt);
    $(btn).removeAttr('id');
    var id = $(btn).attr('id');
    if (id == '')
        return false;
    return true;
}


function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        top: y + 5,
        left: x + 15
    }).appendTo("body").show();
}

function plot (id, history, options, label) {
    $.plot($(id), [history], options);

    var previousPoint = null;
    $(id).bind("plothover", function (event, pos, item) {
        if (item) {
            if (previousPoint != item.datapoint) {
                previousPoint = item.datapoint;

                $("#tooltip").remove();
                var x = new Date(item.datapoint[0]),
                    y = item.datapoint[1];

                showTooltip(item.pageX, item.pageY,
                            x.getDate()+' '+x.getMonthName()+': '+y+' '+label);
            }
        } else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    });
}