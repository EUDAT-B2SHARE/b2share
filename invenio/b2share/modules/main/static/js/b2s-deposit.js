/*
 * This file is part of B2SHARE.
 * Copyright (C) 2013 EPCC, The University of Edinburgh.
 *
 * B2SHARE is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * B2SHARE is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with B2SHARE; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */

$(document).ready(function() {
    "use strict";

    $('#domains input:radio').addClass('visuallyhidden');

    /**
     * Handle clicking on deposit button.
     *
     * Either return success page or errors with form.
     */
    function deposit_click_handler(e) {
        e.preventDefault();
        change_deposit_button_state('depositing');
        var addmeta_url = $("#url_for_addmeta").attr("value");
        $.post(addmeta_url, $("#metaform_form").serialize(),
            function(data) {
                if (data.valid) {
                    // redirect to new url location, with history
                    window.location.href = data.newurl;
                } else {
                    //Just replace metadata form with errors
                    $('#meta-fields').html(data.html);
                    change_deposit_button_state('ready');
                }

            }, "json");
    }

    /**
     * Handle clicking on domain.
     *
     * Should get appropriate metadata form.
     */
    function domain_click_handler(e) {
        var inputEl = $(this).find('input');
        if (!inputEl.prop('checked')) {
            inputEl.prop('checked', true);
            $('#domains .domain').removeClass('highlight-icon');
            $('#domains .domain img').addClass('desaturate');
            $(this).addClass('highlight-icon');
            $(this).find('img').removeClass('desaturate');

            var getform_url = $("#url_for_getform").attr("value");
            if (getform_url[getform_url.length - 1] !== '/') {
                getform_url += getform_url + "/";
            }
            $.get(getform_url + inputEl.val(),
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

    function b2drop_login_handler(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var data = {
            username: $('#b2dropModal #nickname').val(),
            password: $('#b2dropModal #password').val(),
        };
        $.post('/b2deposit/b2drop', data, b2drop_render_handler);
    }

    function b2drop_render_handler(response) {
        $("#b2dropModal #login").hide();
        var div = $("#b2dropModal #files");
        var files = response.files;
        for (var i = 0; i < files.length; i++) {
            div.append(b2drop_render_file(files[i]));
        }
        alert(JSON.stringify(response));
    }

    function b2drop_render_file(f) {
        // TODO: check XSS
        return (
            "<div class='row'>"+
            "<div class='col-xs-4'>"+f.name+"</div>"+
            "<div class='col-xs-4'>"+f.size+"</div>"+
            "<div class='col-xs-4'>"+new Date(f.mtime).toString()+"</div>"+
            "</div>"
        );
    }

    function b2drop_select_handler() {
        alert("select");
    }

    $('#b2drop-login').click(b2drop_login_handler);
    $('#b2drop-select').click(b2drop_select_handler);


    // the url values are put into html by the flask template renderer
    b2share_init_plupload('#fileupload',
        $("#url_for_upload").attr("value"),
        $("#url_for_delete").attr("value"),
        $("#url_for_get_file").attr("value"));

    // dynamic selection
    $('#metaform_form').submit(function() {
        var select_list = this.getElementsByTagName('select');
        for(var i=0; i<select_list.length; i++) {
            var otherOption =  $(select_list[i]).val();
            if(otherOption == "other"){
                // replace select value with text field value
                otherOption.val($("#"+select_list[i]+"_input").val());
            }
        }
    });

    // tooltips for domains
    $("[rel='tooltip']").tooltip({
        position: {
            my: "right center",
            at: 'left-20 center',
            of: '#projects'
        }
    });
});


/**
 * Changes the deposit button and status message based on state.
 * State can be one of: 'ready', 'nofile', 'uploading', 'depositing'
 */
function change_deposit_button_state(state) {
    "use strict";

    if (state === 'ready') {
        $('#deposit').removeClass('disabled').attr('disabled', null).show();
        $('#depositmsg').css('display', 'none');
    } else if (state === 'nofile') {
        $('#deposit').addClass('disabled').attr('disabled', 'disabled').show();
        $('#depositmsg').css('display', 'inline').text('Please select files for upload');
    } else if (state === 'uploading') {
        $('#deposit').addClass('disabled').attr('disabled', 'disabled').show();
        $('#depositmsg').css('display', 'inline').text('Please wait until files are fully uploaded');
    } else if (state === 'depositing') {
        $('#deposit').addClass('disabled').attr('disabled', 'disabled').hide();
        $('#depositmsg').css('display', 'inline').text('Depositing, please wait...');
    } else {
        throw 'Unknown change_deposit_button_state state argument';
    }
}


//removed db_files for simplicity - add restarting later if reqd
function b2share_init_plupload(selector, url, delete_url, get_file_url) {
    "use strict";

    var uploader = new plupload.Uploader({
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
        var state = 'ready';
        if (!uploader.files.length) {
            state = 'nofile';
        } else {
            $.each(uploader.files, function(i, file) {
                if (file.loaded < file.size) {
                     state = 'uploading';
                }
            });
        }
        change_deposit_button_state(state);
    }

    uploader.init();
    setDepositBtnState();

    $('#uploadfiles').click(function(e) {
        $('#uploadfiles').hide();

        uploader.start();
        setDepositBtnState();

        $('#stopupload').show();
        $('#domains').removeClass('hide');
        $('#domains').slideDown();
        e.preventDefault();
    });

    $('#stopupload').click(function(d){
        $('#stopupload').hide();

        uploader.stop();

        $('#uploadfiles').show();
        $.each(uploader.files, function(i, file) {
            if (file.loaded < file.size){
                $("#" + file.id + "_rm").show();
                $('#' + file.id + " .progress-bar").css('width', "0%");
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
                            filename: file.name,
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
        $('#' + file.id + " .progress-bar").css('width', file.percent + "%");
        setDepositBtnState();
    });

    uploader.bind('UploadFile', function(up, file) {
        $('#' + file.id + "_rm").hide();
        setDepositBtnState();
    });

    function splitFileNameExtension(filename) {
        function endsWith(str, suffix) {
            return str.indexOf(suffix, str.length - suffix.length) !== -1;
        }
        var ext = "";
        if (endsWith(filename, ".tar.gz")) {
            ext = ".tar.gz";
        } else if (endsWith(filename, ".tar.bz2")) {
            ext = ".tar.bz2";
        } else {
            var arr = filename.split(".");
            if (arr.length > 1) {
                ext = "." + arr.pop();
            }
        }
        if (filename === ext || ext === ".") {
            ext = "";
        }
        var name = filename.substring(0, filename.length - ext.length);
        return {
            "name": name,
            "ext": ext
        };
    }

    uploader.bind('FilesAdded', function(up, files) {
        var no_files_with_content = true;

        for (var t = files.length - 1; t >= 0; t--) {
            if (files[t].size === 0) {
                alert("File " + files[t].name + " is empty");
                uploader.removeFile(files[t]);
                files.splice(t, 1);
            } else if (files[t].size > 0) {
                no_files_with_content = false;
            }
        }
        if (no_files_with_content === true) {
            setDepositBtnState();
            return;
        }

        var hashmap = {};
        $.each(uploader.files, function(i, file) {
            if (hashmap[file.name]) {
                var split = splitFileNameExtension(file.name);
                var name = split.name, ext = split.ext;
                var suffix = 1;
                while (hashmap[name +"_" + suffix + ext]) {
                    suffix ++;
                }
                var oldname = file.name;
                file.name = name +"_" + suffix + ext;
            }
            hashmap[file.name] = true;
        });

        $('#uploadfiles').removeClass("disabled");
        $('#file-table').show('slow');
        $.each(files, function(i, file) {
            $('#filelist').append(
                '<tr id="' + file.id + '" style="display:none;z-index:-100;">' +
                '<td id="' + file.id + '_link">' + file.name + '</td>' +
                '<td>' + plupload.formatSize(file.size) + '</td>' +
                '<td width="30%"><div class="progress"><div class="progress-bar progress-bar-striped active" style="width: 0%;"></div></div></td>' +
                '<td><a id="' + file.id + '_rm" class="rmlink"><i class="glyphicon glyphicon-trash"></i></a></td>' +
                '</tr>');
            $('#filelist #' + file.id).show('fast');
            $('#' + file.id + '_rm').on("click", function(event){
                uploader.removeFile(file);
                setDepositBtnState();
            });
        });
        setDepositBtnState();
    });

    uploader.bind('FileUploaded', function(up, file, responseObj) {
        $('#' + file.id + " .progress-bar").removeClass("active");
        $('#' + file.id + " .progress-bar").css('width', "100%");
        $('#' + file.id + '_rm').show();
        $('#' + file.id + '_link').html('<a href="' + get_file_url + "?filename=" + responseObj.response + '">' + file.name + '</a>');
        file.unique_filename = responseObj.response;
        if (uploader.total.queued === 0) {
            $('#stopupload').hide();
        }

        $('#uploadfiles').addClass('disabled');
        $('#uploadfiles').show();
        $('#deposit').addClass('btn-primary');
        setDepositBtnState();
    });
}
