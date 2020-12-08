var boton = document.getElementById('intento');
var progreso = 0;

jQuery('#intento').click(function(){
    let valor = $('#img-uploader').val();
    console.log("se ejecuto mi jquery");
    uploadFile(valor);
});

function uploadFile(valor){
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
        url: '/ID',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          console.log("success docuento arriba");
          console.log(data.response);
          if(data.response=="No es una INE"){
            alert(data.response);
          }else if(data.response=="Esa INE ya esta registrada"){
            alert(data.response);
          }
          else if(data.response=="INE registrada exitosamente"){
            progreso= progreso + 25;
            $("#progress").css("width",progreso+"%");
            $("#progress").text(progreso+"%");
            alert(data.response);
          }
          else if(data.response=="Imgen no legible"){
            alert(data.response);
          }
          
        },

    });
}


var boton2 = document.getElementById('intentotraser');
boton2.addEventListener("click",function (){

alert("Documento subido correctamente")
    
});

jQuery('#intentotraser').click(function(){
    let valor = $('#img-traser').val();
    console.log("se ejecuto mi jquery");
    uploadFile2(valor);
});

function uploadFile2(valor){
    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('img-traser').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('img-traser').files[x]);
    }

    $.ajax({
        url: '/IDR',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
            console.log("success documento arriba");
            console.log(data.response);
            if(data.response=="No es una INE"){
              alert(data.response);
            }else if(data.response=="Esa INE ya esta registrada"){
              alert(data.response);
            }
            else if(data.response=="INE registrada exitosamente"){
              progreso= progreso + 25;
              $("#progress").css("width",progreso+"%");
              $("#progress").text(progreso+"%");
              alert(data.response);
            }
            else if(data.response=="Imgen no legible"){
              alert(data.response);
            }
            
          },

    });
}

var boton3 = document.getElementById('intentocompro');
boton3.addEventListener("click",function (){

alert("Documento subido correctamente")
    
});

jQuery('#intentocompro').click(function(){
    let valor = $('#img-compro').val();
    console.log("se ejecuto mi jquery");
    uploadFile3(valor);
});

function uploadFile3(valor){
    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('img-compro').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('img-compro').files[x]);
    }

    $.ajax({
        url: '/COMP',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
            console.log("success documento arriba");
            console.log(data.response);
            if(data.response=="Documento invalido"){
              alert(data.response);
            }else if(data.response=="Imgen no legible"){
              alert(data.response);
            }
            else if(data.response=="Comprobante valido"){
              progreso= progreso + 25;
              $("#progress").css("width",progreso+"%");
              $("#progress").text(progreso+"%");
              alert(data.response);
            }
            
          },

    });
}

var boton4 = document.getElementById('intentoselfie');
boton4.addEventListener("click",function (){

alert("Documento subido correctamente, Ahora Tienes la medalla de documentos")
    
});

jQuery('#intentoselfie').click(function(){
    let valor = $('#img-selfi').val();
    console.log("se ejecuto mi jquery");
    uploadFile4(valor);
});

function uploadFile4(valor){
    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('img-selfi').files.length;
				
    if(ins == 0) {
        $('#msg').html('<span style="color:red">Select at least one file</span>');
        return;
    }

    for (var x = 0; x < ins; x++) {
        form_data.append("files[]", document.getElementById('img-selfi').files[x]);
    }

    $.ajax({
        url: '/SELF',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          console.log("success documento arriba");
          console.log(data);
          progreso= progreso + 25;
          $("#progress").css("width",progreso+"%");
          $("#progress").text(progreso+"%");
        },

    });
}


