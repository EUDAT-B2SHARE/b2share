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

    $('#filelist .file-delete').click(function(){
        var $label = $(this);
        var state = $label.find('input').is(':checked');
        $label.closest('tr').toggleClass('to-delete', state);
    });

    function update_deposit_click_handler(e) {
        e.preventDefault();
        var updatemeta_url = $("#url_for_updatemeta").attr("value");
        $.post(updatemeta_url, $("#metaform_form").serialize(),
            function(data) {
                if (data.valid) {
                    // redirect to new url location, with history
                    window.location.href = data.newurl;
                } else {
                    //Just replace metadata form with errors
                    $('#meta-fields').html(data.html);
                }

            }, "json");
    }

    $('#update_deposit').click(update_deposit_click_handler);

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

    // the bootstrap tooltips
    $("[rel='tooltip']").tooltip({
        placement: 'left',
    });

});
