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

  //var socket = io.connect("https://h2938366.stratoserver.net/" + namespace);
  var socket = io.connect("http://localhost:5000/" + namespace);

  // Timer-Code
  var timerValue = 5;

  function startTimer() {
    var display = document.querySelector('#timer');
    display.textContent = timerValue;

    var timerInterval = setInterval(function () {
      timerValue--;

      if (timerValue >= 0) {
        display.textContent = timerValue;
      } else {
        clearInterval(timerInterval);
        sendSnapshot();
      }
    }, 1000);
  }

  function sendSnapshot() {
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    var video = document.querySelector('#videoElement');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    var dataURL = canvas.toDataURL('image/jpeg');

    var userRef = document.getElementById('user-data');
    var attribute = userRef.getAttribute('data-user');

    var jsonString = attribute.replace(/'/g, '"')
    var jsonObj = JSON.parse(jsonString)

    var request = new XMLHttpRequest();
    request.open('POST', '/verifypicture')
    request.setRequestHeader('Content-Type', 'application/json');

    var data = {
      username: jsonObj.username,
      image: dataURL
    };
    var json = JSON.stringify(data);

    request.onload = function () {
      if(request.status === 200)
      {
        console.log("Picture has been send successfully");
        var response = JSON.parse(request.responseText)
        var url = new URL(response.redirect, window.location.href);
        for (var key in response.data) {
          url.searchParams.append(key, response.data[key]);
        }
        window.location.href = url.href;
      }
      else
        console.log("Error while sending picture: ", request.status)
    };

    request.send(json);

    //var link = document.createElement('a');
    //link.href = dataURL;
    //link.download = 'snapshot.jpeg';
    //link.click();
  }

  // Starte den Timer beim Laden der Seite
  startTimer();


  

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
