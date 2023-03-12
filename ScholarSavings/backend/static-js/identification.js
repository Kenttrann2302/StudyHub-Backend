// Create the logic to render the box for identification number depends on the option of the user

window.onload = function() {
  const default_value = "1";
  const idType = document.getElementById('id_type');
  const message = document.getElementById('message');
  const idNumber = document.getElementById('id_number');


  idType.value = default_value;

  idType.addEventListener('change', function() {
    // if the option is student email address
    if(this.value === "2"){
      idNumber.setAttribute("type", "text");
      idNumber.setAttribute("name", "id_number");
      idNumber.setAttribute("max-length", 50);
      idNumber.style.display = 'inline-block';
      message.innerHTML = "To verify using your student email address, enter your school email address into the provided input field. This email address should be an official school email address that ends in .edu or .ac (depending on your school). Once you submit the email address, we will send you a verification email to confirm that you are a student at your school."
    }
    
    // if the option is student id card
    else if (this.value === "3"){
      idNumber.setAttribute("type", "file");
      idNumber.setAttribute("name", "verification_file");
      idNumber.setAttribute("accept", "image/png, image/jpeg, image/jpg, application/pdf")
      idNumber.style.display = 'inline-block';
      message.innerHTML = "To verify using your student ID card, take a photo of your school-issued student ID card and upload it using the provided file upload file. The photo should clearly show your name, photo, and the name of your school. If you are unable to take a photo of your ID card, you may also upload a scanned copy of your ID card.";
    }

    // if the option is an enrollment verification letter
    else if(this.value === "4"){
      idNumber.setAttribute("type", "file");
      idNumber.setAttribute("name", "verification_file");
      idNumber.setAttribute("accept", "image/png, image/jpeg, image/jpg, application/pdf")
      idNumber.style.display = 'inline-block';
      message.innerHTML = "To verify using an enrollment verification letter, obtain a letter from your school's registrar or admissions office that confirms your enrollment status. This letter should include your name, the name of your school, your enrollment status (full-time, part-time, etc.), and the date the letter was issued. Once you have the letter, scan or take a photo of it and upload it using the provided file upload field."
    }

    // if the option is a transcript
    else if(this.value === "5"){
      idNumber.setAttribute("name", "verification_file");
      idNumber.setAttribute("accept", "image/png, image/jpeg, image/jpg, application/pdf")
      idNumber.style.display = 'inline-block';
      message.innerHTML = "To verify using a transcript, obtain an official transcript from your school's registrar or admissions office. This transcript should include your name, the name of your school, your program of study, and your enrollment status. Once you have the transcript, scan or take a photo of it and upload it using the provided file upload field."
    }

    else {
      idNumber.style.display = 'none';
      message.innerHTML = "";
    }
  });
};

