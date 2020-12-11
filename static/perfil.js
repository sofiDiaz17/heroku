var btn= document.getElementById('enviar')
var btn1= document.getElementById('intento')
btn.addEventListener("click",function (){

    alert("Contrato enviado a su correo")
        
    });

btn1.addEventListener("click",function (){

    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('img-uploader').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('img-uploader').files[x]);
    }
    document.getElementById("loader").style.display = 'block';
    $.ajax({
        url: '/uploadContract',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
            document.getElementById("loader").style.display = 'none';
          alert("Contrato subido exitosamente")
          window.location.href = "/perfil";

          
        },
        error: function (){
            document.getElementById("loader").style.display = 'none';
            alert("No se pudo subir el contrato")
        }

    });
        
    }); 

    jQuery('#envcontrato').click(function(){
        console.log("botón enviar contrato");
        sendContract();
    });

    function sendContract(){
        //console.log("llego  a mi funcion 2")
    
        $.ajax({
            url: '/sendContract',
            type: 'POST',
            contentType: false,
            processData: false,
            showLoader: true,
            dataType: 'json',
            success: function (data) {
              console.log("success docuemtno arriba");
              print(data)
              
            },
            error: function (){
                console.log("NO SE PUDO")
            }
    
        });
    }
    

    
   