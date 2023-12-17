// navbar.js
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    // Define your navigation bar HTML here or render it from a template
    const navbarHTML = `
<nav class="black">
  <div class="nav-wrapper">
    <a href="#" class="brand-logo white-text">Logo</a>
    <ul id="nav-mobile" class="right hide-on-med-and-down">
      <li><a href="#" class="waves-effect waves-light btn white black-text">Home</a></li>
      <li><a href="#" class="waves-effect waves-light btn white black-text">About</a></li>
      <li><a href="#" class="waves-effect waves-light btn white black-text">Corp Intel</a></li>
      <!-- Add more list items/buttons as needed -->
    </ul>
  </div>
</nav>
    `;
    res.send(navbarHTML);
});

module.exports = router;
