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

    $.ajax({
        url: '/uploadContract',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          alert("Contrato subido exitosamente, ahora tienes la medalla de contrato")
        },

    });
        
    }); 

    jQuery('#envcontrato').click(function(){
        console.log("botón enviar contrato");
        sendContract();
    });

    function sendContract(){
        console.log("llego  a mi funcion 2")
    
        $.ajax({
            url: '/sendContract',
            type: 'POST',
            contentType: false,
            processData: false,
            showLoader: true,
            dataType: 'json',
            success: function (data) {
              console.log("success docuemtno arriba");
              
            },
    
        });
    }
    

    
   