// Return to the homepage if the users click on the logo or the header
function goToHomePage() {
 window.location.href = "http://127.0.0.1:5000/home/";
}

document.addEventListener("DOMContentLoaded", function(event) {
 // Add event listener to the header logo
 var logo = document.querySelector(".logo");
 logo.addEventListener("click", function() {
  goToHomePage();
 });
});

// function redirect the users to the search url when the event is being detected
const searchIcon = document.getElementsByClassName("search");

searchIcon.addEventListener("click", () => {
 window.location.href = "http://127.0.0.1:5000/hcm/search";
});