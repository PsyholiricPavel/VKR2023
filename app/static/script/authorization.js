var main = function(){
$('.message a').click(function(){
    $('.register-form').animate({height: "toggle", opacity: "toggle"}, "slow");
    $('.login-form').animate({height: "toggle", opacity: "toggle"}, "slow");
 });
 $('.input-file input[type=file]').on('change', function(){
	let file = this.files[0];
	$(this).closest('.input-file').find('.input-file-text').html(file.name);
});
}
$(document).ready(main);
$(document).ready(main_2);
