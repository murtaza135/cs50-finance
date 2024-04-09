// Displays whether a username is available or not in register using AJAX
$(document).ready(function () {
  if (((document.getElementById("register_form") === null || document.getElementById("register_form") === undefined) ? true : false) == false) {
    var username = document.getElementById("register_form").username;
    username.onkeyup = function () {
      if (username.value.length == 0) {
        document.getElementById("register_username_hint").style.display = "none";
        document.getElementById("register_username_hint").innerHTML = "";
        return;
      }

      else {
        $.getJSON("/register_username_hint", { "username": username.value }, function (data) {
          document.getElementById("register_username_hint").innerHTML = data.message;
          document.getElementById("register_username_hint").style.display = "inline-block";
          if (data.message == "Username is available") {
            document.getElementById("register_username_hint").style.color = "green";
          }
          else {
            document.getElementById("register_username_hint").style.color = "red";
          }
        });
      }
    };
  }
});

// Get information about new quote price and display it on index using AJAX
document.body.onload = function () {
  $(document).ready(function () {
    setInterval(function () {
      var i;
      var index_rows = document.getElementsByClassName("index_row");

      for (i = 0; i < index_rows.length; i++) {
        JSON_data = index_rows[i].childNodes[1].innerHTML;
        $.getJSON("/index_price_refresh", { "symbol": JSON_data }, (function (reference_i) {
          return function (data) {
            index_rows[reference_i].childNodes[5].innerHTML = data.price;
          };
        }(i)));
        // When you just declare i at the top, and leave it at that, the call back function runs AFTER the loop has finished, therefore the value of i no longer remains what you intended it to be
        // therefore, you must create a new function and pass in a parameter which HOLDS the value of i, but, itself, is NOT i
        // so when we pass in reference_i, it holds the value of i, but is not i itslef, therefore it will NOT change as the loop continues
        // and thus when the callback function runs, it will use the original value of i through reference_i
        // even whilst i continues to change and finish the loop
      }
    }, 1800000 /* 30 minutes */);
  });
};

// get a list of symbols which match the beginning of a valid symbol, or match the entire symbol, and display a list of them
function symbol_search_filter(trigger_object) {
  $(document).ready(function () {
    var a = trigger_object.parentNode.getElementsByTagName("a");
    var search_box = trigger_object;

    // if there is nothing in the search box, then hide all options
    if (search_box.value.length == 0) {
      // hide all <a> tags
      for (var i = 0; i < 10; i++) {
        a[i].style.display = "none";
        search_box.style.backgroundColor = "white";
      }
      return;
    }

    else {
      // send out ajax request for 10 values
      $.getJSON("/symbol_search_filter", { "search_box_value": search_box.value.toUpperCase() }, function (data) {

        // if less than 10 values have returned, hide the remaining <a> tags
        if (data.length != 10) {
          for (var i = data.length; i < 10; i++) {
            a[i].style.display = "none";
          }
        }

        // put data into the innerHTML of the <a> tags, and display them, with some style attributes
        for (var i = 0; i < data.length; i++) {
          a[i].innerHTML = data[i].symbol.toUpperCase();
          a[i].href = "#" + data[i].symbol.toUpperCase();
          a[i].style.display = "block";
          a[i].style.borderBottom = "none";
          search_box.style.backgroundColor = "#f1f1f1";
        }

        if (data.length > 0) {
          a[(data.length) - 1].style.borderBottom = "1px solid #ddd";
        }

        if (data.length <= 0) {
          search_box.style.backgroundColor = "white";
        }
      });
    }
  });
}

$(document).ready(function () {
  $(".search_box").click(function () {
    symbol_search_filter(this);
  });

  $(".search_box").keyup(function () {
    symbol_search_filter(this);
  });
});
