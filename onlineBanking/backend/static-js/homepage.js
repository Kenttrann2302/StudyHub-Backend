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