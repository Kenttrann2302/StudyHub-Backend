// Create the logic to render the box for identification number depends on the option of the user: Passport or Driver License

window.onload = function() {
  const default_value = "1";
  const idType = document.getElementById('id_type');
  const message = document.getElementById('message');
  const idNumber = document.getElementById('id_number');


  idType.value = default_value;

  idType.addEventListener('change', function() {
    if(this.value === "2"){
      idNumber.setAttribute('maxlength', 9);
      idNumber.style.display = 'inline-block';
      message.innerHTML = "Please enter the 9 digits passport number located on the first page:"
    }
    else if (this.value === "3"){
      idNumber.setAttribute('maxlength', 5);
      idNumber.style.display = 'inline-block';
      message.innerHTML = "Please enter the 5 digits driver license number located on the front face:"
    }
    else {
      idNumber.style.display = 'none';
      message.innerHTML = "";
    }
  });
};

