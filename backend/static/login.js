document.querySelector('.form').addEventListener('submit', function(event) {
  event.preventDefault(); // Prevent the form from submitting and refreshing the page

  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;

  console.log('Username:', username);
  console.log('Password:', password);

  fetch('http://127.0.0.1:6543/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Server Response:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });

});