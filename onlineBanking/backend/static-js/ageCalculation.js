// function calculate the age of the user depends on the birthday input
function calculateAge() {
  var birthday = new Date(document.getElementById("birthday").value);
  var ageDifMs = Date.now() - birthday.getTime();
  var ageDate = new Date(ageDifMs)
  var age = Math.abs(ageDate.getUTCFullYear() - 1970);
  document.getElementById("age").innerHTML = age;
  document.getElementById("age-input").value = age;
};

document.getElementById("birthday").addEventListener("change", calculateAge);

// after the users submit the form
document.querySelector("#signupform").addEventListener("submit", function(event) {
  event.preventDefault();
  // send the age to the server as a hidden html element that has the value of the span element
  document.querySelector("#signupform").submit();
});


