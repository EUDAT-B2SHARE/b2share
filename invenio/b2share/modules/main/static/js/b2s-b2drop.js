/*
 * This file is part of B2SHARE.
 */

$(document).ready(function() {
    "use strict";

    var ajaxData = {};

    var b2dropUploadURL = $("#url_for_b2drop_upload").attr("value");

    function log() {
        window['console'].log(arguments);
    }

    function login_handler(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        ajaxData = {
            username: $('#b2dropModal #nickname').val(),
            password: $('#b2dropModal #password').val(),
            path: "/",
        };
        $("#b2dropModal #login").hide();
        $("#b2dropModal #wait").show();
        $("#b2dropModal #files").hide();
        $.post('/b2deposit/b2drop/list', ajaxData, render_handler);
    }

    function render_handler(response) {
        $("#b2dropModal #login").hide();
        $("#b2dropModal #wait").hide();
        $("#b2dropModal #files").show();
        var table = $("#b2dropModal #files table");
        table.show();
        table.empty();
        var header = $("<tr><th>File name</th><th>Size</th><th class='date'>Date</th></tr>");
        table.append(header);
        render_subdir_handler(header, 0, response);
    }

    function render_subdir_handler(headrow, indent, response) {
        var fs = response.files;
        fs.reverse();
        fs.forEach(add_table_line.bind(null, headrow, indent, false));
        fs.forEach(add_table_line.bind(null, headrow, indent, true));
    }

    function add_table_line(headrow, indent, onlydirs, f) {
        if ((!f.isdir && onlydirs) || (f.isdir && !onlydirs)) {
            return;
        }
        var el = render_file(indent, f);
        headrow.after(el);
        el.attr('data-path', f.path);
        el.click(table_line_handler.bind(null, el, indent, f));
    }

    function table_line_handler(row, indent, f) {
        if (f.isdir) {
            ajaxData.path = f.path;
            $.post('/b2deposit/b2drop/list', ajaxData,
                render_subdir_handler.bind(null, row, indent+1));
        } else {
            var input = row.find('input');
            var newstate = !input.prop('checked');
            input.prop('checked', newstate);
            row.toggleClass('selected');
        }
    }

    function render_file(indent, f) {
        // TODO: check XSS
        var indentspan = "<span style='margin-left:"+ (50*indent) +"px'></span>";
        var icon = "";
        if (f.isdir) {
            icon = "<span class='glyphicon glyphicon-folder-close' aria-hidden='true'> </span> ";
        } else {
            icon = "<input type='checkbox' name='sel' value='"+f.path+"'> ";
        }
        var ret = "<tr>"+
            "<td>"+indentspan+icon+f.name+"</td>"+
            "<td>"+(f.size||"")+"</td>"+
            "<td class='date'>"+new Date(f.mtime).toLocaleString()+"</td>"+
            // "<td>"+f.mtime+"</td>"+
        "</tr>";
        return $(ret);
    }

    function select_handler() {
        var selected = $("#b2dropModal #files table tr input:checked").parent().parent();
        selected.each(function() {
            var path = $(this).attr('data-path');
            ajaxData.path = path;
            var file = {id:path, name: path, size:0};
            addFile(file, 'uploading...');
            $.post(b2dropUploadURL, ajaxData,
                addFile.bind(null, file, 'uploaded'));
        });
    }

    function addFile(file, msg) {
        $('#file-table-b2drop').show('slow');
        var file_el = $(
            '<tr id="' + file.id + '" style="display:none;z-index:-100;">' +
            '<td id="' + file.id + '_link">' + file.name + '</td>' +
            '<td>' + file.size + '</td>' +
            '<td width="30%">'+msg+'</td>' +
            '<td><a id="' + file.id + '_rm" class="rmlink"><i class="glyphicon glyphicon-trash"></i></a></td>' +
            '</tr>');
        $('#filelist-b2drop').append(file_el);
        file_el.show('fast');
    }

    $('#b2dropModal').modal();
    $('#b2drop-login').click(login_handler);
    $('#b2drop-select').click(select_handler);
});
