// function calculate the age of the user depends on the birthday input
function calculateAge() {
  // calculate the age from the user's birthday
  debugger;
  var birthday = new Date(document.getElementById("birthday").value);
  var ageDifMs = Date.now() - birthday.getTime();
  var ageDate = new Date(ageDifMs);
  var age = Math.abs(ageDate.getUTCFullYear() - 1970);
  document.getElementById("age").innerHTML = age;
  return age;
};

// after the users submit the form
document.getElementById("signupform").addEventListener("submit", function(event) {
  event.preventDefault();

  // send the age to the server using an AJAX request
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "{{ url_for(createAccount) }}", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.onreadystatechange = function () {
    if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
      // handle the response from the server
    }
  };
  document.getElementById("hidden-age").value = calculateAge()
  xhr.send(calculateAge());
});


