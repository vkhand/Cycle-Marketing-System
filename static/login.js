$(document).ready(function() {
  $(".ui.form").form({
    fields: {
      email: {
        identifier: "username",
        rules: [
          {
            type: "empty",
            prompt: "Please enter your username"
          }
        ]
      },
      password: {
        identifier: "password",
        rules: [
          {
            type: "empty",
            prompt: "Please enter your password"
          }
        ]
      }
    }
  });
});
