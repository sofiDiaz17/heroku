
//var boton = document.getElementById('intento');
var progreso = document.getElementById("progreso").offsetWidth;
/*
jQuery('#intento').click(function(){
    let valor = $('#img-uploader').val();
    console.log("se ejecuto mi jquery");
    uploadFile(valor);
});
*/

$('#img-uploader').change(function(e){ 
  let valor = $('#img-uploader').val();
  console.log("se ejecuto mi jquery para INE");
  uploadFile(valor);
}); 
function uploadFile(valor){
    console.log("llego  a mi funcion")
    document.getElementById("llamda").style.display='block';
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
           // alert(data.response);
            document.getElementById("mensajeError").innerHTML="No es una INE";
            document.getElementById("error-box").style.display="block";
            document.getElementById("llamda").style.display = 'none';
          }else if(data.response=="Esa INE ya esta registrada"){
            //alert(data.response);
            document.getElementById("mensajeError").innerHTML="Esa INE ya esta registrada";
            document.getElementById("error-box").style.display="block";
            document.getElementById("llamda").style.display = 'none';
          }
          else if(data.response=="INE registrada exitosamente"){
            progreso= progreso + 25;
            $("#progreso").css("width",progreso+"%");
            //$("#progreso").text(progreso+"%");
            document.getElementById("textoBien").innerHTML="INE registrada exitosamente";
            document.getElementById("success-box").style.display="block"
            //alert(data.response);
            document.getElementById("llamda").style.display = 'none';
            document.getElementById("cargar").style.visibility="visible";
          }
          else if(data.response=="Imgen no legible"){
            //alert(data.response);
            document.getElementById("mensajeError").innerHTML="Imgen no legible";
            document.getElementById("error-box").style.display="block";
            document.getElementById("llamda").style.display = 'none';
           

          }
          
        },

    });
}

/*
var boton2 = document.getElementById('intentotraser');
boton2.addEventListener("click",function (){
alert("Documento subido correctamente") 
});

jQuery('#intentotraser').click(function(){
    let valor = $('#img-traser').val();
    console.log("se ejecuto mi jquery");
    uploadFile2(valor);
});
*/


$('#img-traser').change(function(e){ 
  let valor = $('#img-traser').val();
  console.log("se ejecuto mi jquery para INE ATRAS");
  uploadFile2(valor);
}); 
function uploadFile2(valor){
  console.log("llego  a mi funcion")
  var form_data = new FormData();
  var ins = document.getElementById('img-traser').files.length;
  document.getElementById("llamda").style.display='block';
      
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
          document.getElementById("llamda").style.display = 'none';
          if(data.response=="No es una INE"){
            //alert(data.response);
            document.getElementById("mensajeError").innerHTML="No es una INE";
            document.getElementById("error-box").style.display="block";
            document.getElementById("llamda").style.display = 'none';
          }else if(data.response=="Esa INE ya esta registrada"){
            //alert(data.response);
            document.getElementById("mensajeError").innerHTML="Esa INE ya esta registrada";
            document.getElementById("error-box").style.display="block";
            document.getElementById("llamda").style.display = 'none';
          }
          else if(data.response=="INE registrada exitosamente"){
            progreso= progreso + 25;
            $("#progreso").css("width",progreso+"%");
            document.getElementById("textoBien").innerHTML="INE registrada exitosamente";
            document.getElementById("success-box").style.display="block"
            //$("#progreso").text(progreso+"%");
            //alert(data.response);
            document.getElementById("llamda").style.display = 'none';
            document.getElementById("cargar2").style.visibility="visible";
          }
          else if(data.response=="Imgen no legible"){
           // alert(data.response);
            document.getElementById("mensajeError").innerHTML="Imgen no legible";
            document.getElementById("error-box").style.display="block";
            document.getElementById("llamda").style.display = 'none';
            

          }
          
        },

  });
};


/*
var boton3 = document.getElementById('intentocompro');
boton3.addEventListener("click",function (){

//alert("Documento subido correctamente")
    
});

jQuery('#intentocompro').click(function(){
    let valor = $('#img-compro').val();
    console.log("se ejecuto mi jquery");
    uploadFile3(valor);
});*/
$('#img-compro').change(function(e){ 
  let valor = $('#img-compro').val();
  console.log("se ejecuto mi jquery COMPROBANTE");
  uploadFile3(valor);
}); 
function uploadFile3(valor){
    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('img-compro').files.length;
    document.getElementById("llamda").style.display='block';
				
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
            document.getElementById("llamda").style.display = 'none';
            if(data.response=="Documento invalido"){
              //alert(data.response);
              document.getElementById("mensajeError").innerHTML="Documento invalido";
              document.getElementById("error-box").style.display="block";
              document.getElementById("llamda").style.display = 'none';
            }else if(data.response=="Imgen no legible"){
              //alert(data.response);
              document.getElementById("mensajeError").innerHTML="Imgen no legible";
              document.getElementById("error-box").style.display="block";
              document.getElementById("llamda").style.display = 'none';
            }
            else if(data.response=="Comprobante valido"){
              progreso= progreso + 25;
              $("#progreso").css("width",progreso+"%");
             // $("#progreso").text(progreso+"%");
             document.getElementById("textoBien").innerHTML="Comprobante valido";
             document.getElementById("success-box").style.display="block"
              //alert(data.response);
              document.getElementById("llamda").style.display = 'none';
              document.getElementById("cargar3").style.visibility="visible";

            }
            
          },

    });
}

/*
var boton4 = document.getElementById('intentoselfie');
boton4.addEventListener("click",function (){

alert("Documento subido correctamente, Ahora Tienes la medalla de documentos")
    
});

jQuery('#intentoselfie').click(function(){
    let valor = $('#img-selfi').val();
    console.log("se ejecuto mi jquery");
    uploadFile4(valor);
});*/
$('#img-selfi').change(function(e){ 
  let valor = $('#img-selfi').val();
  console.log("se ejecuto mi jquery SELFIE");
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
  document.getElementById("llamda").style.display = 'block';
  $.ajax({
      url: '/SELF',
      type: 'POST',
      contentType: false,
  processData: false,
      data:form_data,
      showLoader: true,
      dataType: 'json',
      success: function (data) {
        //console.log("success documento arriba");
        console.log(data.response);
        if(data.response=="No hay rostros"){
          document.getElementById("mensajeError").innerHTML="No hay rostros";
          document.getElementById("error-box").style.display="block";
          document.getElementById("llamda").style.display = 'none';
          //alert(data.response);
        }else if(data.response=="No hay coincidencia"){
          //alert(data.response);
          document.getElementById("mensajeError").innerHTML="No hay coincidencia";
          document.getElementById("error-box").style.display="block";
          document.getElementById("llamda").style.display = 'none';
        }
        else if(data.response=="No subio su INE"){
         // alert(data.response);
          document.getElementById("mensajeError").innerHTML="No subio su INE";
          document.getElementById("error-box").style.display="block";
          document.getElementById("llamda").style.display = 'none';
        }
        else if(data.response=="Documento Valido"){
          progreso= progreso + 25;
          $("#progress").css("width",progreso+"%");
          document.getElementById("llamda").style.display = 'none';
          document.getElementById("textoBien").innerHTML="Documento valido";
          document.getElementById("success-box").style.display="block"
         // $("#progress").text(progreso+"%");
          //alert(data.response);
          document.getElementById("cargar4").style.visibility="visible";
        }
      }
  });
}

/*
function uploadFile4(valor){
    console.log("llego  a mi funcion")
    var form_data = new FormData();
    var ins = document.getElementById('img-selfi').files.length;
    document.getElementById("llamda").style.display='block';
				
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
          console.log(progreso)

          progreso= progreso + 25;
          $("#progreso").css("width",progreso+"%");
          //$("#progreso").text(progreso+"%");
          console.log(progreso)

          document.getElementById("llamda").style.display = 'none';
          document.getElementById("cargar4").style.visibility="visible";
         // $("#cargar4").show();
          //document.getElementById("cargar4").style.display = 'block';
          console.log("mostrar paloma")
        },

    });
}
*/

