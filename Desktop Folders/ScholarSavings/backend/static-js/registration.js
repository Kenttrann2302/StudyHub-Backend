// Create the logic to render the box for registration method depends on the option of the user

window.onload = function () {
 const idType = document.getElementById('id_type');
 const default_value = "1";
 const message = document.getElementById('message');
 const verification_method = document.getElementById('verification_method');
 const areaCodeMessage = document.getElementById('area-code-label');
 const areaCode = document.getElementById('area-code');

 idType.value = default_value;
 

 idType.addEventListener('change', function() {
  // if the option is an email address
  if(this.value === "2") {
   areaCodeMessage.style.display = 'none';
   areaCode.style.display = 'none';
   verification_method.setAttribute("type", "text");
   verification_method.setAttribute("max-length", 50);
   verification_method.style.display = 'inline-block';
   message.innerHTML = "Please enter your email address in the box below:";
  }

  // if the option is phone number
  else if (this.value === "3"){
   areaCodeMessage.style.display = 'inline-block';
   areaCode.style.display = 'block';
   verification_method.setAttribute("type", "text");
   verification_method.setAttribute("max-length", 10);
   verification_method.style.display = 'inline-block';
   message.innerHTML = 'Please enter your area code and phone number below:';
  }

  else {
   areaCodeMessage.style.display = 'none';
   areaCode.style.display = 'none';
   verification_method.style.display = 'none';
   message.innerHTML = "";
  }
 });
};