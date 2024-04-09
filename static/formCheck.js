// Validate login form
$(function () {
  $("#login_form").submit(function () {
    if (!this.username.value) {
      flash_message("Must provide username");
      return false;
    }

    else if (!this.password.value) {
      flash_message("Must provide password");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate register form
$(function () {
  $("#register_form").submit(function () {
    if (!this.username.value) {
      flash_message("Must provide username");
      return false;
    }

    else if (!this.password.value) {
      flash_message("Must provide password");
      return false;
    }

    else if ((this.password.value).length < 8) {
      flash_message("Password must be atleast 8 characters long");
      return false;
    }

    else if (!this.confirmation.value) {
      flash_message("Must provide confirmation");
      return false;
    }

    else if (this.password.value != this.confirmation.value) {
      flash_message("Passwords do not match! Please re-enter your password");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate quote form
$(function () {
  $("#quote_form").submit(function () {
    if (!this.symbol.value) {
      flash_message("Must provide stock symbol");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate buy form
$(function () {
  $("#buy_form").submit(function () {
    if (!this.symbol.value) {
      flash_message("Must provide stock symbol");
      return false;
    }

    else if (!this.shares.value) {
      flash_message("Must provide number of shares");
      return false;
    }

    else if (this.shares.value <= 0) {
      flash_message("Must provide valid number of shares");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate sell form
$(function () {
  $("#sell_form").submit(function () {
    if (!this.symbol.options.selectedIndex) {
      flash_message("Please select a symbol");
      return false;
    }

    else if (!this.shares.value) {
      flash_message("Please enter number of shares");
      return false;
    }

    else if (this.shares.value <= 0) {
      flash_message("Must provide valid number of shares");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate change_password form
$(function () {
  $("#change_password_form").submit(function () {
    if (!this.old_password.value) {
      flash_message("Please enter your old password");
      return false;
    }

    else if (!this.new_password.value) {
      flash_message("Please enter your new password");
      return false;
    }

    else if ((this.new_password.value).length < 8) {
      flash_message("Password must be atleast 8 characters long");
      return false;
    }

    else if (!this.confirmation.value) {
      flash_message("Please confirm your new password");
      return false;
    }

    else if (this.new_password.value != this.confirmation.value) {
      flash_message("Passwords do not match! Please re-enter your password");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate delete form
$(function () {
  $("#delete_form").submit(function () {
    if (!this.password.value) {
      flash_message("Please enter your password");
      return false;
    }

    else if ((this.password.value).length < 8) {
      flash_message("Please enter your password");
      return false;
    }

    else if (!this.confirmation.value) {
      flash_message("Please confirm your password");
      return false;
    }

    else if (this.password.value != this.confirmation.value) {
      flash_message("Passwords do not match! Please re-enter your password");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});

// Validate selling and buying stocks from index
$(function () {
  $(".index-button").submit(function () {
    if (!this.shares.value) {
      flash_message("Please enter number of shares");
      return false;
    }

    else if (this.shares.value <= 0) {
      flash_message("Must provide valid number of shares");
      return false;
    }

    else {
      disable_submit_button();
      return true;
    }
  });
});
