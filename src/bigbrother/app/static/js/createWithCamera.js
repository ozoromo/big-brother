$(document).ready(function() {
    let namespace = "/createWithCamera";
    let video = document.querySelector("#videoElement");
    let canvas = document.querySelector("#canvasElement");
    let ctx = canvas.getContext('2d');
    photo = document.getElementById('photo');
    var localMediaStream = null;
    var ready = true;

    // TODO: Edit
    var socket = io.connect("http://localhost:5000" + namespace);

    function sendSnapshot() {
        if (!localMediaStream) {
            return;
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        let dataURL = canvas.toDataURL('image/jpeg');

        socket.emit('input_image_create', dataURL);
        socket.emit('output image')

        var img = new Image();
        socket.on('out-image-event',function(data){
            ready = true;

            img.src = dataURL
            photo.setAttribute('src', data.image_data);

            // TODO: Why is this commented out?
            //socket.emit('input image', dataURL);
        });
    }

    socket.on('connect', function() {
        console.log('Connected!');
    });

    socket.on('redirect', function (data) {
        console.log(data.url);
        window.location = data.url;
    });

    var constraints = {
        video: {
            width: { min: 640 },
            height: { min: 480 }
        }
    };

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        video.srcObject = stream;
        localMediaStream = stream;

        socket.emit('start_transfer_create')

        socket.on('ack_transfer', function() {
            setInterval(function () {
                if (ready){
                    sendSnapshot();
                    ready = false;
                }
            }, 1000);
        });

    }).catch(function(error) {
        console.log(error);
    });
});
