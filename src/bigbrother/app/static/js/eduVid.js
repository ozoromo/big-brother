const video = document.getElementById('eduVid-element');

function onTimeStampClick(button)
{
    const time = button.value;
    if(isNaN(time)) return;
    console.log("setting time: " + time)
    video.currentTime = button.value;
}