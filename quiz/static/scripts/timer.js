class Timer {
  var timeInterval;

  constructor() {
    this.timeInterval = setInterval(function() {return false;}, 0);
  }

  function getTimeRemaining(totaltime, endtime) {
    var t = endtime - ServerDate.now();
    var seconds = Math.round((t / 1000) % 60);
    var minutes = Math.round((t / 1000 / 60) % 60);
    var hours = Math.round((t / (1000 * 60 * 60)) % 24);
    var days = Math.round(t / (1000 * 60 * 60 * 24));
    return {
      'total': t,
      'days': days,
      'hours': hours,
      'minutes': minutes,
      'seconds': seconds,
    };
  };

  function initializeClockWithData(id, data) {
    clearInterval(this.timeInterval);
    if(!isNaN(data.timerLength) && data.timerLength > 0) {
      var waitInterval = setInterval(function()
      {
        if (ServerDate.is_synchronized()) {
          clearInterval(waitInterval);
          var timerEnd = new ServerDate(ServerDate.parse(new ServerDate(data.timerEnd)));
          var timerLength = parseFloat(data.timerLength);
          return initializeSyncedClock(id, timerEnd, timerLength, timeInterval);
        }
      }, 500);
    }
  };

  function initializeClock(id, endtime, timerLength) {
    clearInterval(this.timeInterval);
    if(data.timerLength && data.timerLength > 0) {
      var waitInterval = setInterval(function()
      {
        if (ServerDate.is_synchronized()) {
          clearInterval(waitInterval);
          return initializeSyncedClock(id, timerEnd, timerLength, timeInterval);
        }
      }, 500);
    }
  };

  function initializeSyncedClock(id, endtime, timerLength) {
    const clock = document.getElementById(id);
    const minutesSpan = clock.querySelector('.minutes');
    const secondsSpan = clock.querySelector('.seconds');
    endtime = ServerDate.parse(endtime);
    console.log(endtime);
    var totaltime = endtime - ServerDate.now();
    var totaltimeSeconds = totaltime/1000;
    console.log(totaltimeSeconds);
    if(totaltimeSeconds > timerLength || (timerLength > 0 && totaltimeSeconds < 0)) {
      totaltime = timerLength * 1000;
      endtime = ServerDate.now() + totaltime;
      console.log(totaltime);
    }
    if(timerLength <= 0 || isNaN(endtime) || totaltime <= 0) {
      clock.style.display = "none";
      return false;
    }
    else {
      clock.style.display = "block";
    }
    $("#" + id + " .progress-bar").finish().css("width","100%").animate({
      width: "0%"
    }, totaltime, "linear");

    function updateClock() {
      var t = getTimeRemaining(totaltime, endtime);

      if (t.total <= 0) {
        minutesSpan.innerHTML = ('00');
        secondsSpan.innerHTML = ('00');
        clearInterval(this.timeInterval);
      }
      else {
        minutesSpan.innerHTML = ('0' + t.minutes).slice(-2);
        secondsSpan.innerHTML = ('0' + t.seconds).slice(-2);
      }
    }

    updateClock();
    this.timeInterval = setInterval(updateClock, 1000);
  };
}
