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
