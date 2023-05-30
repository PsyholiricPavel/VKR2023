var main = function() {
  $('.open-menu').click(
    function() {
      $('.menu').animate({left: '0px'}, 200);
      $('.dropdown').animate({left: '290px'}, 200)
    });
 
  $('.close-menu').click(
    function() {
      $('.menu').animate({left: '-285px'}, 200);
      $('.dropdown').animate({left: '5px'}, 200)
    });
};

$(document).ready(main);
$(document).ready(main_2);