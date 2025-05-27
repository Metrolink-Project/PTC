function handleFile(files) {
  if (files.length > 0) {
      const file = files[0];
      
      // Sending `file` to a backend using fetch
      const formData = new FormData();
      formData.append("file", file);
      
      fetch("http://127.0.0.1:6543/upload", {
      method: "POST",
      body: formData,
      })
      .then(res => res.text())
      .then(result => alert(result))
      .catch(err => alert("Upload failed: " + err));
  }
}

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

  fetch('http://127.0.0.1:6543/index')
  .then((response) => {
      if (!response.ok) {
          throw new Error(`HTTP Error: ${response.status}`);
      }
      return response.text();
  })
  .then((html) => {

    document.body.innerHTML = html;
  
  })
  .catch((error) => {
      console.error(error);
  });

});