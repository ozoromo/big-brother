$(document).ready(function(){
    const video = document.querySelector("video");
    const originalWebcamCanvas = document.querySelector("#originalWebcamCanvas");
    const gestureCanvas = document.querySelector("#gestureCanvas");
    gestureCanvas.width = video.videoWidth;
    gestureCanvas.height = video.videoHeight;

    var socket = io.connect("https://" + document.domain + ":" + location.port + "/gesture_recognition_text");

    setInterval(function(){
        originalWebcamCanvas.width = video.videoWidth;
        originalWebcamCanvas.height = video.videoHeight;
        originalWebcamCanvas.getContext('2d').drawImage(
            video, 0, 0, originalWebcamCanvas.width, originalWebcamCanvas.height
        );

        var dataURL = originalWebcamCanvas.toDataURL("image/jpeg");
        socket.emit("gesture_recognition_text", {image: dataURL});
    }, 700);

    socket.on("ack_gesture_recognition_text", function(image) {
        gestureCanvas.width = video.videoWidth;
        gestureCanvas.height = video.videoHeight;
        var ctx = gestureCanvas.getContext("2d");
        var img = new Image;
        img.onload = function(){
            ctx.drawImage(img, 0, 0, gestureCanvas.width, gestureCanvas.height);
        };
        img.src = image["image"];
    });

    navigator.mediaDevices.getUserMedia( {audio: false, video: true })
    .then(stream => video.srcObject = stream)
    .catch(error => console.error(error));
});
