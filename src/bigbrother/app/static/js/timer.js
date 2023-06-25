var timerValue = 3;

function startTimer() {
  var display = document.querySelector('#timer');
  display.textContent = timerValue;

  var timerInterval = setInterval(function () {
    timerValue--;

    if (timerValue >= 0) {
      display.textContent = timerValue;
    } else {
      clearInterval(timerInterval);
    }
  }, 1000);
}

// Starte den Timer beim Laden der Seite
window.onload = function () {
  startTimer();
};