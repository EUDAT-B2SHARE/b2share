$(document).ready(function() {
  $('#submit-deposit').click(function(evt) {

    var filearr = [];
    $(".uploaded a").each(function() { 
      filearr.push($(this).attr('title'));
    });

    //Note this requires IE8+
    $('#filelist').val(JSON.stringify(filearr));

  });
  $('#domains input:radio').addClass('visuallyhidden');
  $('#domains .domain').click(function() {
    $(this).addClass('highlight-icon').siblings().removeClass('highlight-icon');
  });

});

//removed db_files for simplicity - add restarting later if reqd
function simplestore_init_plupload(selector, url, delete_url, get_file_url) {

    uploader = new plupload.Uploader({
        // General settings
        runtimes : 'html5',
        url : url,
        max_file_size : '460mb',
        chunk_size : '1mb',
        //unique_names : true,
        browse_button : 'pickfiles',
        drop_element : 'filebox'

        // Specify what files to browse for
        //filters : [
        //    {title : "Image files", extensions : "jpg,gif,png,tif"},
        //    {title : "Compressed files", extensions : "rar,zip,tar,gz"},
        //    {title : "PDF files", extensions : "pdf"}
        //]
    });

    uploader.init();

    $('#uploadfiles').click(function(e) {
        uploader.start();
        $('#uploadfiles').hide();
        $('#stopupload').show();
        e.preventDefault();
    });

    $('#stopupload').click(function(d){
        uploader.stop();
        $('#stopupload').hide();
        $('#uploadfiles').show();
        $.each(uploader.files, function(i, file) {
            if (file.loaded < file.size){
                $("#" + file.id + "_rm").show();
                $('#' + file.id + " .bar").css('width', "0%");
            }
        });
    });

    uploader.bind('FilesRemoved', function(up, files) {
        $.each(files, function(i, file) {
            $('#filelist #' + file.id).hide('fast');
            if (file.loaded == file.size) {
                $.ajax({
                    type: "POST",
                    url: delete_url,
                    data: $.param({
                        filename: file.unique_filename
                    })
                });
            }
        });
        if(uploader.files.length === 0){
            $('#uploadfiles').addClass("disabled");
            $('#file-table').hide('slow');
        }
    });

    uploader.bind('UploadProgress', function(up, file) {
        $('#' + file.id + " .bar").css('width', file.percent + "%");
        console.log("Progress " + file.name + " - " + file.percent);
    });

    uploader.bind('UploadFile', function(up, file) {
        $('#' + file.id + "_rm").hide();
    });


    uploader.bind('FilesAdded', function(up, files) {
        $('#uploadfiles').removeClass("disabled");
        $('#file-table').show('slow');
        $.each(files, function(i, file) {
            $('#filelist').append(
                '<tr id="' + file.id + '" style="display:none;z-index:-100;">' +
                '<td id="' + file.id + '_link">' + file.name + '</td>' +
                '<td>' + plupload.formatSize(file.size) + '</td>' +
                '<td width="30%"><div class="progress progress-stri´ped active"><div class="bar" style="width: 0%;"></div></div></td>' +
                '<td><a id="' + file.id + '_rm" class="rmlink"><i class="icon-trash"></i></a></td>' +
                '</tr>');
            $('#filelist #' + file.id).show('fast');
            $('#' + file.id + '_rm').on("click", function(event){
                uploader.removeFile(file);
            });
        });
    });

    uploader.bind('FileUploaded', function(up, file, responseObj) {
        console.log("Done " + file.name);
        $('#' + file.id + " .progress").removeClass("progress-striped");
        $('#' + file.id + " .bar").css('width', "100%");
        $('#' + file.id + '_rm').show();
        $('#' + file.id + '_link').html('<a href="' + get_file_url + "?filename=" + responseObj.response + '">' + file.name + '</a>');
        file.unique_filename = responseObj.response;
        if (uploader.total.queued === 0)
            $('#stopupload').hide();

        $('#uploadfiles').addClass('disabled');
        $('#uploadfiles').show();

    });
}
