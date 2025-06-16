function handleFile() {
    fetch('http://127.0.0.1:6543/upload', {
        method: 'POST',
        headers: {
            'Content-Length': '0'
        }
    })
    .then(res => res.text())
    .then(result => alert(result))
    .catch(err => alert("Upload failed: " + err));
}

document.querySelector('.form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the form from submitting and refreshing the page
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    console.log('Username:', username);
    console.log('Password:', password);

    try {
        const response = await fetch('http://127.0.0.1:6543/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        });

        const data = await response.json();

        if (data === 'Wrong password') {
            alert('Wrong password. Please try again.');
            return; // Stop execution if password is wrong
        }

        console.log('Server Response:', data);

        // If the password is correct, proceed with the second fetch
        const indexResponse = await fetch('http://127.0.0.1:6543/index');

        if (!indexResponse.ok) {
            throw new Error(`HTTP Error: ${indexResponse.status}`);
        }

        const html = await indexResponse.text();
        document.body.innerHTML = html;

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred.');
    }
});