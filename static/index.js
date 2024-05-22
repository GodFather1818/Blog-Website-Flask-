document.addEventListener("DOMContentLoaded", function () {

    let instagram = document.getElementById("Instagram");
    instagram.addEventListener("click", redirect_to_Instagram);
  
    let linkedin = document.getElementById("LinkedIn");
    linkedin.addEventListener("click", redirect_to_LinkedIn);
  
    let facebook = document.getElementById("Facebook");
    facebook.addEventListener("click", redirect_to_Facebook);



    function redirect_to_Instagram() {
        instagramUrl = "https://www.instagram.com/Sahilshah837/";
        window.open(instagramUrl, '_blank');
      }
      function redirect_to_Facebook() {
        facebookUrl =
          "https://www.facebook.com/profile.php?id=100060396642674&mibextid=ZbWKwL/";
          window.open(facebookUrl, '_blank');
    
      }
      function redirect_to_LinkedIn() {
        linkedinUrl = "https://www.linkedin.com/in/sahil-shah-907b60242/";
        window.open(linkedinUrl, '_blank');
      }
});