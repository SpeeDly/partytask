var FILES_TO_SUBMIT = []; // 2D index-->file
var ALLOWED_FILES_TYPES = ["image/jpeg"]; //contain only allowed file's type
var file_number = 0; //the count of all files
var all_context = [];
var all_images = [];
var all_src = [];


$("#id_picture").on("change", function(){
    previewImage(this);
});

//reendering all images
    function drawImages(){
        for(var i=0, len=FILES_TO_SUBMIT.length; i<len; i++){
            var canvas = document.getElementById("pic_" + FILES_TO_SUBMIT[i][0]);
            var context = canvas.getContext('2d');
            var img_obj = new Image();
            img_obj.src = all_src[i];
            all_images.push(img_obj);
            all_context.push(context);
        }

        all_images[all_images.length-1].onload = function() {
            for(var i=0, len=all_images.length; i<len; i++){
                if (all_images[i].width>all_images[i].height)
                    all_context[i].drawImage(all_images[i], 0, 0, all_images[i].width, all_images[i].height, 0, 0, 85, 65);
                else{
                    all_context[i].drawImage(all_images[i], 0, 0, all_images[i].width, all_images[i].height, 0, 0, 65, 85);
                }
            }
            all_context = [];
            all_images = [];
        }
    }

//add element to #uploaded
    function displayElements(){
        
        $ ("#gallery_preview").html("");

        for(var i=0, len=FILES_TO_SUBMIT.length; i<len; i++)
        {
            var file = FILES_TO_SUBMIT[i][1];

            var element_id = FILES_TO_SUBMIT[i][0]; 
            var html_el = '<li class="ready_photo" data-send="'+ element_id +'">'
            html_el += '<canvas id="pic_' + element_id + '" width="85" height="85"/>'
            html_el += '<ul class="info"><li>' + file.name + '</li><li>' + file.size + '</li></ul>'
            html_el += '<ul class="action"><li class="delete">Delete</li><li class="cover_photo">Use as cover photo</li></ul>'
            $ ("#gallery_preview").html($ ("#gallery_preview").html() + html_el);
        }
        drawImages();
    }

//on input change
    function previewImage(input){

        files = input.files;

        for (var i = 0; i < files.length; i++)
        {

            if(isValid(files[i]))
            {

                FILES_TO_SUBMIT.push([file_number, files[i]])
                file_number++;

                var reader = new FileReader();
                reader.onload = function(e) {
                    var src = e.target.result;
                    all_src.push(src);
                }
                    reader.readAsDataURL(files[i]);
            }
        }
        drawCanvasImage();
    }

//execute the code when all files are loaded
    function drawCanvasImage(){
        timeId = setInterval(function(){
            if(all_src.length == FILES_TO_SUBMIT.length)
            {
                displayElements();
                clearInterval(timeId);
            }
        },500)
    }

//make validation
    function isValid(file)  {
        // var extension = file.type.toLowerCase();
        // if (ALLOWED_FILES_TYPES.indexOf(extension) == -1)
        //  return false;
        // else return true;
        return true;
    }


// delete img from the #uploaded
$("#gallery_preview").on("click", ".delete", function(){
    var file_index = $(this).closest(".ready_photo").data("send");
    $(this).closest(".ready_photo").hide(600, function() {
        $(this).remove()
    });

    for(var i=0, len=FILES_TO_SUBMIT.length; i<len; i++)
        if (file_index == FILES_TO_SUBMIT[i][0]){
            FILES_TO_SUBMIT.splice(i, 1);
            all_src.splice(i,1)
        }
});

//Upload picture
$('#step_4').submit(function(e) {

    $('body').append("<div class='uploading waiting'></div>")
    $('.uploading').css({
        "height": $(document).height(),
        "width": $(document).width()
    });

    var data, xhr;
    data = new FormData();

    data.append("csrfmiddlewaretoken", $(this).find("[name='csrfmiddlewaretoken']").val());
    
    xhr = new XMLHttpRequest();
    
    xhr.open( 'POST', 'http://glamfame.com:8000/salons/gallery/', true );

    for (var i = 0; i < FILES_TO_SUBMIT.length; i++)
    {
        data.append('file', FILES_TO_SUBMIT[i][1]);
    }

    xhr.onreadystatechange = function ( response ) { window.location.replace('http://' + window.location.host + '/salons/settings/profile') };

    xhr.send( data );

    e.preventDefault();

    });