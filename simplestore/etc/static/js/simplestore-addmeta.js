$(document).ready(function() {
    json = $.parseJSON($("#filelist").val());
    filetable = $("#filetable");
    $.each(json, function(index, file) {
      filetable.append("<input name='fileinputs' type='text' disabled value='" + file + "'/>");
    });
});
