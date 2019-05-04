// Correct enter press in Bootstrap modal forms
$(document).keypress(function(e) {
  if (e.keycode == 13 || e.which == 13) {
    if ($("#sign-up-modal").hasClass("show")) {
      e.preventDefault();
      $("#sign-up-button").click();
    }
    if ($("#sign-in-modal").hasClass("show")) {
      e.preventDefault();
      $("#sign-in-button").click();
    }
    if ($("#crud-modal").hasClass("show")) {
      e.preventDefault();
      $("#crud-button").click();
    }
  }
});

$("#sign-out-link").click(function(e) {
  e.preventDefault();
  userSignOut();
});

// Reset error validation whenever the sign in/up modals are shown
$("#sign-up-modal").on("show.bs.modal", function(event) {
  $("#sign-up-form").removeClass("was-validated");
});
$("#sign-in-modal").on("show.bs.modal", function(event) {
  $("#sign-in-form").removeClass("was-validated");
});

// Generic implementation of the a CRUD modal
$("#crud-modal").on("show.bs.modal", function(event) {
  var src = $(event.relatedTarget); // Button that triggered the modal
  var modal = $(this);
  // Hide text box for delete actions
  if (/delete/i.test(src.data("crud-title"))) {
    $("#crud-value").css("display", "none");
  } else {
    $("#crud-value").css("display", "block");
  }
  $("#crud-title").text(src.data("crud-title"));
  $("#crud-label").text(src.data("crud-label"));
  $("#crud-value").attr("placeholder", src.data("crud-placeholder"));
  $("#crud-value").val(src.data("crud-value"));
  $("#crud-button").text(src.data("crud-button"));
  $("#crud-button").attr("onclick", src.data("crud-function"));
  $("#crud-title").text(src.data("crud-title"));
});

// Sign in button event handler
$("#sign-in-button").click(function(event) {
  // If form in invalid then show errors and exit
  if ($("#sign-in-form")[0].checkValidity() === false) {
    $("#sign-in-form").addClass("was-validated");
    return;
  }
  $("#sign-in-form").addClass("was-validated");
  // First things first, disable the sign in button
  loadingOn();
  // Attempt sign in
  signInAction();
});

// Sign up button event handler
$("#sign-up-button").click(function(event) {
  // Attempt sign up
  signUpAction1();
});

// Reset sign up username validation whenever changed
$("#username-up").keyup(function() {
  // Username in the sign up form is checked for duplication
  //  and so the error is sometimes might be changed
  //  and so it has to be reset
  if ($("#username-up").val() != "") {
    // If the field is not empty clear the validation error
    $("#username-up")[0].setCustomValidity("");
    $("#username-up-error").html("Please provide a valid username");
  } else {
    // Other wise revert to the original validation error
    $("#username-up-error").html("Please provide a valid username");
    $("#username-up")[0].setCustomValidity("Username required");
  }
});

// Checks that passwords match
function checkPassMatch() {
  if ($("#password-up-1").val() == $("#password-up-2").val()) {
    $("#password-up-2")[0].setCustomValidity("");
  } else {
    $("#password-up-2")[0].setCustomValidity("Passwords must match");
  }
  if ($("#password-up-1").val() != "" && $("#password-up-2").val() != "") {
    $("#sign-up-form").addClass("was-validated");
  }
}

// Check password match while typing
$("#password-up-1").keyup(checkPassMatch);
$("#password-up-2").keyup(checkPassMatch);
