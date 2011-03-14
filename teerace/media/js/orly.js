/*
 *      orly.js
 *      Robert Chmielowiec 2011
 */


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
