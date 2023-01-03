$('form').submit(function(event) {
  event.preventDefault();
  
  // Serialize the form data
  var formData = $(this).serialize();
  
  // Send a POST request to the server-side script
  $.post('/login', formData, function(response) {
    if (response == 'success') {
      // Login was successful, redirect the user
      window.location = '/dashboard';
    } else {
      // Login failed, display an error message
      $('#error-message').text('Invalid email or password').show();
    }
  });
});