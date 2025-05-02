<h1>Secure SMS Application</h1>
<ul>The goal in the developing of this project was to create an online application that would securely send messages across the internet between users. The content of the messages would only be known to the users, and securely stored using assymetric encryption</ul>


<h2> Features </h2>
  <ul>
    <li>Messenger-style chat interface (contacts on the left, chat on the right)</li>
    <li>End-to-end encryption using RSA (WIP)</li>
    <li>Public key sharing via server, private key stored only in browser (WIP)</li>
    <li>Seamless real-time messaging experience</li>
    <li>Persistent conversations and message history</li>
    <li> Built with Flask (Python backend) and modern JavaScript (frontend) </li>

</ul>

<h2> How It Works </h2>

<h3> Encryption Model </h3>
  <ul>
    <li>Key Generation: Each user generates an RSA key pair on first use</li>
    <li>Public Key: Uploaded to the server for other users to access</li>
    <li>Private Key: Securely stored in the browser using `IndexedDB`, never sent to server</li>
    <li> Message Flow: Messages are encrypted with recipient's public key before sending, and then messages are decrypted with the user's private key upon receiving</li>
  </ul>
<h3> Technologies Used</h3>
  <ul>
    <li>Backend was built using Flask and Python</li>
    <li>Frontend was built using HTML, CSS, and JavaScript</li>
    <li>Crypto was made with Web Crypto API (RSA-OAEP)</li>
    <li>Local Storage uses SQLite to store user and message information</li>
    <li>UI Layout is made using CSS Flexbox and Grid in combination with BULMA.css</li>

  </ul>

<h2>Project Location</h2>
<ul> Currently this is hosted via a RENDER server. First time visit takes a while to boot. Find the application here: https://spring25-cis434-sms.onrender.com/</ul>

