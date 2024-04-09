// fade elements out (javascript)
function fade_js(element) {
  var op = 1;  // initial opacity
  var timer = setInterval(function () {
    if (op <= 0.1) {
      clearInterval(timer);
      document.getElementById(element).style.display = 'none';
    }
    document.getElementById(element).style.opacity = op;
    document.getElementById(element).style.filter = 'alpha(opacity=' + op * 100 + ")";
    op -= op * 0.1;
  }, 300);
}

// fade elements out (jQuery)
$.fn.fade = function (element) {
  $(element).delay(5000).fadeOut(3000);
};

// Automatically fade out any success or info flash messages from flask
$(function () {
  $(".alert-success").delay(5000).fadeOut(3000);
  $(".alert-info").delay(5000).fadeOut(3000);
});
