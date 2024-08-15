const video = document.getElementById('eduVid-element');

function onTimeStampClick(button)
{
    const time = button.value;
    if(isNaN(time)) return;
    console.log("setting time: " + time)
    video.currentTime = button.value;
}

function onSubmitVideo(event)
{
    const infoBox= document.getElementById("upload-info")
    infoBox.style.display = "inherit"
    const uploadButton = document.getElementById("upload-button")
    if(uploadButton !== null)
        uploadButton.disabled = true;
}

const form = document.getElementById("submit-form");
form?.addEventListener('submit', onSubmitVideo);