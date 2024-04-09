// Close flash message when button clicked by user
$(function () {
  $("#flash_button_id").click(function () {
    $("#flash_border_id").css("display", "none");
  });
});

// Display Flash Messages
function flash_message(message, fade_out = "no_fade") {

  document.getElementById("flash_message_id").innerHTML = message;

  document.getElementById("flash_message_id").style.color = "#D8000C";
  document.getElementById("flash_border_id").style.backgroundColor = "#FFD2D2";

  document.getElementById("flash_border_id").style.opacity = 1;
  document.getElementById("flash_border_id").style.display = "block";


  if (fade_out == "fade_out") {
    $.fn.fade("#flash_border_id");
  }
}

// Ensure forms do not have multiple submissions
function disable_submit_button() {
  $(".submit-button").prop("disabled", true);

  setTimeout(function () {
    $(".submit-button").prop("disabled", false);
  }, 10000);
}

// If user clicks on an option in the quote/buy search box, then put that value into the search box
function put_into_search_box(trigger_object) {
  // put value of option into search box
  var search_box = trigger_object.parentNode.childNodes[1];
  search_box.value = trigger_object.innerHTML;

  // hide all <a> tags
  var a = trigger_object.parentNode.getElementsByTagName("a");
  for (var i = 0; i < 10; i++) {
    a[i].style.display = "none";
    console.log(a[i].style.display);
    search_box.style.backgroundColor = "white";
  }
}

$(function () {
  $(".search_option").click(function () {
    put_into_search_box(this);
  });
});

// If user clicks anywhere outside of the search box or the list of options (i.e <div id="myDropdownQuote">), then hide all options
document.addEventListener("click", function (event) {
  if (document.getElementsByClassName("dropdown-content").length == 1) {
    if (event.target.closest(".dropdown-content")) {
      return;
    }

    else {
      var a = document.getElementsByClassName("dropdown-content")[0].getElementsByTagName("a");
      var search_box = document.getElementsByClassName("dropdown-content")[0].childNodes[1];

      for (var i = 0; i < 10; i++) {
        a[i].style.display = "none";
        search_box.style.backgroundColor = "white";
      }
    }
  }
});

// Adding redirect links to the buttons on "/quoted"
$(function () {
  $("#quote_button_one").click(function () {
    location.href = '/quote';
  });

  $("#quote_button_two").click(function () {
    location.href = '/';
  });
});
