var boton = document.getElementById('intento');
var progreso = 0;
boton.addEventListener("click",function (){

alert("Documento subido correctamente")
    
});

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
        url: '/B',
        type: 'POST',
        contentType: false,
		processData: false,
        data:form_data,
        showLoader: true,
        dataType: 'json',
        success: function (data) {
          console.log("success docuemtno arriba");
          console.log(data);
         
        },

    });
}