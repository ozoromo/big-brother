/**
 * @Author: Julius U. Heller <thekalk>
 * @Date:   2021-06-14T13:12:57+02:00
 * @Project: ODS-Praktikum-Big-Brother
 * @Filename: main.js
 * @Last modified by:   Julius U. Heller
 * @Last modified time: 2021-06-20T13:33:30+02:00
 */



$(document).ready(function(){
  let namespace = "/webcamJS";
  let video = document.querySelector("#videoElement");
  let canvas = document.querySelector("#canvasElement");
  let ctx = canvas.getContext('2d');
  photo = document.getElementById('photo');
  var localMediaStream = null;
  var ready = true;

  var socket = io.connect("https://h2938366.stratoserver.net:443" + namespace);
  //var socket = io.connect("http://localhost:5000" + namespace);

  function sendSnapshot() {
    if (!localMediaStream) {
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    //ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, 300, 150);
    ctx.drawImage(video, 0, 0);

    let dataURL = canvas.toDataURL('image/jpeg');
    socket.emit('input_image_login', dataURL);

    socket.emit('output image')
    //socket.emit('server ready')

    var img = new Image();
    socket.on('next_image',function(data){
    ready = true;


    img.src = dataURL//data.image_data
    photo.setAttribute('src', data.image_data);

    //socket.emit('input image', dataURL);

    });

    socket.on('ready',function(data){

    ready = true;

    });

    socket.on('display_image',function(data){
    ready = true;

    img.src = dataURL//data.image_data
    photo.setAttribute('src', data.image_data);
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

    socket.emit('start_transfer_login')

    socket.on('ack_transfer', function() {
      setInterval(function () {
        if (ready){
          sendSnapshot();
          ready = false;
        }
      }, 200);
    });

  }).catch(function(error) {
    console.log(error);
  });
});
