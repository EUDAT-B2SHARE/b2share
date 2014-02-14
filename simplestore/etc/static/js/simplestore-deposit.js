/*
 * This file is part of SimpleStore.
 * Copyright (C) 2013 EPCC, The University of Edinburgh.
 *
 * SimpleStore is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * SimpleStore is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SimpleStore; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */
$(document).ready(function() {

    $('#domains input:radio').addClass('visuallyhidden');

    /**
     * Handle clicking on deposit button.
     *
     * Either return success page or errors with form.
     */
    function deposit_click_handler(e) {
        e.preventDefault();
        $('#deposit').addClass('disabled');
        $.post("addmeta/" + $('#sub_id').val(), $("#metaform_form").serialize(),
            function(data) {
                if (data.valid) {
                    //Load new page with success message
                    var newDoc = document.open("text/html", "replace");
                    newDoc.write(data.html);
                    newDoc.close();

                } else {
                    //Just replace metadata form with errors
                    $('#meta-fields').html(data.html);
                    $('#deposit').removeClass('disabled');
                }

            }, "json");
    }

    /**
     * Handle clicking on domain.
     *
     * Should get appropriate metadata form.
     */
    function domain_click_handler(e) {
        inputEl = $(this).find('input');
        if (!inputEl.prop('checked')) {
            inputEl.prop('checked', true);
            $('#domains .domain').removeClass('highlight-icon');
            $('#domains .domain img').addClass('desaturate');
            $(this).addClass('highlight-icon');
            $(this).find('img').removeClass('desaturate');

            $.get("/deposit/getform/" + $('#sub_id').val() + "/" + inputEl.val(),
                    function(data) {
                        $('#meta-fields').html(data);
                        $('#submitbutton').removeClass('hide');
                        $('#reqfootnote').removeClass('hide');
                    });
            var form = $('#metaform');
            form.hide();
            form.removeClass('hide');
            form.slideDown();
            $('html,body').animate({scrollTop: form.offset().top}, "slow");
        }
    }

    $('#domains .domain').click(domain_click_handler);
    //Added following two handlers to make clicking easier
    //(misclicks were common before e.g. when mouse went out of focus)
    $('#domains .domain').mousedown(domain_click_handler);
    $('#domains .domain').select(domain_click_handler);

    $('#deposit').click(deposit_click_handler);

});

//removed db_files for simplicity - add restarting later if reqd
function simplestore_init_plupload(selector, url, delete_url, get_file_url) {

        uploader = new plupload.Uploader({
                // General settings
                runtimes : 'html5',
                url : url,
                max_file_size : '2048mb',
                chunk_size : '20mb',
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

        function setDepositBtnState() {
            var nowUploading = false;
            $.each(uploader.files, function(i, file) {
                if (file.loaded < file.size) {
                     nowUploading = true;
                }
            });
            $('#deposit').toggleClass('disabled', nowUploading)
                         .attr('disabled', nowUploading ? 'disabled' : null);
        }

        uploader.init();
        setDepositBtnState();

        $('#uploadfiles').click(function(e) {
            uploader.start();
            setDepositBtnState();

            //Show the domain selection stuff
            $('#uploadfiles').hide();
            $('#stopupload').show();
            $('#domains').removeClass('hide');
            $('#domains').slideDown();
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
                setDepositBtnState();
        });

        uploader.bind('UploadProgress', function(up, file) {
                $('#' + file.id + " .bar").css('width', file.percent + "%");
                setDepositBtnState();
                console.log("Progress " + file.name + " - " + file.percent);
        });

        uploader.bind('UploadFile', function(up, file) {
                $('#' + file.id + "_rm").hide();
                setDepositBtnState();
        });


        uploader.bind('FilesAdded', function(up, files) {
                no_files_with_content = true;
                
                for(var t = files.length-1;t>=0;t--){
                    if(files[t].size == 0){
                        alert("File " + files[t].name + " is empty");
                        $('#filelist #' + files[t].id).hide('fast');
                        files.splice(t,1);
                    }
                    else if(files[t].size>0){
                        no_files_with_content = false;
                    }
                }
                if(no_files_with_content == true){ return; }
                
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
                setDepositBtnState();
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
                $('#deposit').addClass('btn-primary');
                setDepositBtnState();
        });
}
