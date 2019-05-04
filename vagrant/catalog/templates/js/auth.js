// Boolean holding the final log in status
//  used to decide whether to hide or
//  show the edit buttons on the page
var isLoggedIn = false;

// Function to sign out from Google
function gAuthSignOut() {
  var auth2 = gapi.auth2.getAuthInstance();
  auth2.signOut().then(function() {
    console.log("Google user signed out.");
  });
}

// Update display after sign in
function userSignedIn(profilePicture) {
  $("#sign-out-link").removeClass("d-none");
  $("#sign-in-link").addClass("d-none");
  $("#sign-up-link").addClass("d-none");
  $("#g-signin").addClass("d-none");
  if (profilePicture) {
    $("#profile-picture").attr("src", profilePicture);
    $("#profile-picture").addClass(" d-sm-block");
  }
  isLoggedIn = true;
}

// Sign out and update display accordingly
function userSignOut() {
  // Only sign out if user cookies found
  //  otherwise consider user already
  //  signed out and do nothing
  if (Cookies.get("user_id") && Cookies.get("token")) {
    loadingOn();
    Cookies.remove("user_id");
    Cookies.remove("username");
    Cookies.remove("token");
    $("#sign-out-link").addClass("d-none");
    $("#sign-in-link").removeClass("d-none");
    $("#sign-up-link").removeClass("d-none");
    $("#g-signin").removeClass("d-none");
    $("#profile-picture").removeClass(" d-sm-block");
    $("#profile-picture").attr("src", "");
    gAuthSignOut();
    isLoggedIn = false;
    $.get("/api/v1/catalog", function(data) {
      refreshCatalog(data);
      loadingOff();
    });
  }
}

// Check for login cookies and update HTML
//  Used after document loaded, sign up
//  and sign in
function refreshUser() {
  if (Cookies.get("user_id") && Cookies.get("token")) {
    var user_id = Cookies.get("user_id");
    var token = Cookies.get("token");
    // Make sure of the provided token by reading
    //  user id and which make sure both token and
    //  user id are linked and correct
    $.ajax({
      type: "GET",
      url: "/api/v1/users/" + user_id,
      beforeSend: function(xhr) {
        xhr.setRequestHeader(
          "Authorization",
          "Basic " + btoa(token + ":blank")
        );
      },
      // If saved cookie user is successfully authenticated
      success: function(data) {
        // Update sign in header
        userSignedIn(data.picture);
        // Update catalog to show edit buttons
        $.get("/api/v1/catalog", function(data) {
          refreshCatalog(data);
          loadingOff();
        });
      },
      error: function(data) {
        userSignOut();
      }
    });
  } else {
    userSignOut();
  }
}

// Sign in function
function signInAction(username, password) {
  $.ajax({
    type: "GET",
    url: "/api/v1/token",
    // username: username,
    // password: password,
    beforeSend: function(xhr) {
      xhr.setRequestHeader(
        "Authorization",
        "Basic " + btoa(username + ":" + password)
      );
    },
    success: function(data) {
      if (data.token) {
        Cookies.set("user_id", data.user_id);
        Cookies.set("username", $("#username-in").val());
        Cookies.set("token", data.token, { expires: 1 / 24 });
        // Sign in
        refreshUser();
      } else {
        userSignOut();
      }
    },
    error: function(data) {
      userSignOut();
    }
  });
}

// The sign up process has 4 dependant
//  AJAX stages triggered after the
//  user presses the sign up button and
//  after validating the sign up form
// So I had to split the process into
//  several functions each leading to
//  the next in case of success
// They will be defined in reverse
//  order below knowing that the last
//  AJAX request is refreshUser above

// Fourth stage: fetch token
function signUpAction4() {
  $.ajax({
    type: "GET",
    url: "/api/v1/token",
    username: $("#username-up").val(),
    password: $("#password-up-1").val(),
    success: function(data) {
      if (data.token) {
        Cookies.set("token", data.token, { expires: 1 / 24 });
        // Sign in
        refreshUser();
      } else {
        // Now re-enable the button again
        loadingOff();
      }
    },
    error: function(data) {
      // Now re-enable the button again
      loadingOff();
    }
  });
}

// Third stage: add new user
function signUpAction3() {
  $.ajax({
    type: "POST",
    url: "/api/v1/users",
    contentType: "application/json",
    data: JSON.stringify({
      username: $("#username-up").val(),
      password: $("#password-up-1").val(),
      picture:
        "https://upload.wikimedia.org/wikipedia/commons/e/e0/Anonymous.svg",
      email: ""
    }),
    success: function(data) {
      Cookies.set("user_id", data.id);
      Cookies.set("username", data.username);
      signUpAction4();
    },
    error: function(data) {
      // Now re-enable the button again
      loadingOff();
    }
  });
}
// Second stage: check username duplication
function signUpAction2() {
  $.get(
    "/api/v1/users/check/" + encodeURIComponent($("#username-up").val()),
    function(data) {
      if (data.found == true) {
        $found = true;
        $("#username-up-error").html(
          "Username already exists please choose a new one"
        );
        $("#username-up")[0].setCustomValidity("duplicate username");
        // Now re-enable the button again
        loadingOff();
      } else {
        $("#username-up")[0].setCustomValidity("");
        $("#username-up-error").html("Please provide a valid username");
        signUpAction3();
      }
    }
  );
}
// First stage: check form validity
function signUpAction1() {
  // If form in invalid then show errors and exit
  if ($("#sign-up-form")[0].checkValidity() === false) {
    $("#sign-up-form").addClass("was-validated");
    return;
  }
  $("#sign-up-form").addClass("was-validated");
  // First things first, disable the sign up button
  loadingOn();
  signUpAction2();
}
