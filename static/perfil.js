var btn= document.getElementById('enviar')
var btn1= document.getElementById('intento')
btn.addEventListener("click",function (){
    alert("Contrato enviado a su correo")
});



    $('#contrUp').change(function(e){ 
       
    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('contrUp').files.length;
    document.getElementById("llamda").style.display='block';
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('contrUp').files[x]);
    }

    $.ajax({
        url: '/uploadContract',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
            document.getElementById("textoBien").innerHTML="¡Genial!. Tu contrato se subio exitosamente y por completar tu perfil eres nivel 1. Checa tus recompensas";
            document.getElementById("success-box").style.display="block"
         // alert("¡Genial!. Tu contrato se subio exitosamente y por completar tu perfil eres nivel 1. Checa tus recompensas")
          document.getElementById("llamda").style.display = 'none';
          window.location.href = "/perfil";

        },
        error: function(){
            document.getElementById("mensajeError").innerHTML="Algo salió mal";
            document.getElementById("error-box").style.display="block";
        }

    });
      }); 

btn1.addEventListener("click",function (){

    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('contrUp').files.length;
    document.getElementById("llamda").style.display='block';
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('img-uploader').files[x]);
    }

    $.ajax({
        url: '/uploadContract',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          alert("¡Genial!. Tu contrato se subio exitosamente y por completar tu perfil eres nivel 1. Checa tus recompensas")
          document.getElementById("llamda").style.display = 'none';
          window.location.href = "/perfil";

        },

    });
        
    }); 

    jQuery('#envcontrato').click(function(){
        console.log("botón enviar contrato");
        sendContract();
    });

    function sendContract(){
        console.log("llego  a mi funcion 2")
        document.getElementById("llamda").style.display='block';
    
        $.ajax({
            url: '/sendContract',
            type: 'POST',
            contentType: false,
            processData: false,
            showLoader: true,
            dataType: 'json',
            success: function (data) {
              console.log("success docuemtno arriba");
              document.getElementById("llamda").style.display = 'none';
              
            },
    
        });
    }
    

    
   