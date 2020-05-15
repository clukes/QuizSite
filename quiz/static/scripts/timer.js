  function getTimeRemaining(endtime) {
    var t = Date.parse(endtime) - Date.parse(new Date());
    var seconds = Math.floor((t / 1000) % 60);
    var minutes = Math.floor((t / 1000 / 60) % 60);
    var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
    var days = Math.floor(t / (1000 * 60 * 60 * 24));
    return {
      'total': t,
      'days': days,
      'hours': hours,
      'minutes': minutes,
      'seconds': seconds,
    };
  };

  function initializeClock(id, endtime, timerRemaining, timeInterval) {
    clearInterval(timeInterval);
    var totaltime = Date.parse(endtime) - Date.parse(new Date());
    if(totaltime > timerRemaining || (totaltime < timerRemaining - 5)) {
      totaltime = timerRemaining;
      endtime = Date.parse(new Date()) + timerRemaining;
    }
    const clock = document.getElementById(id);
    const minutesSpan = clock.querySelector('.minutes');
    const secondsSpan = clock.querySelector('.seconds');
    if(isNaN(endtime) || totaltime <= 0) {
      clock.style.display="none";
      return false;
    }
    else {
      clock.style.display="block";
    }
    $("#" + id + " .progress-bar").finish().css("width","100%").animate({
      width: "0%"
    }, totaltime, "linear");

    function updateClock() {
      var t = getTimeRemaining(endtime);

      if (t.total <= 0) {
        minutesSpan.innerHTML = ('00');
        secondsSpan.innerHTML = ('00');
        // progressValue = 0;
        // progress.style.width = progressValue + '%';
        // progress.setAttribute('aria-valuenow', progressValue);
        clearInterval(timeInterval);
      }
      else {
        minutesSpan.innerHTML = ('0' + t.minutes).slice(-2);
        secondsSpan.innerHTML = ('0' + t.seconds).slice(-2);
      }
    }

    updateClock();
    timeInterval = setInterval(updateClock, 1000);
    return timeInterval;
  };
