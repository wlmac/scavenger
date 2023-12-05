const countdown = document.getElementById("countdown")
const eTextPre = document.getElementById("countdown-text-pre")
const eTextPost = document.getElementById("countdown-text-post")

function updateColours(classList, className, contains) {
    if (contains) {
        if (!classList.contains(className)) classList.add(className)
    } else {
        if (classList.contains(className)) classList.remove(className)
    }
}

const sanitizeStart = (text) => text.startsWith('__') ? '' : text;
const sanitizeEnd = (text) => text.startsWith('__') ? '' : text;

const newCalculateTime = (start, end, beforeStartPre, beforeStartPost, endsPre, endsPost, endedPre, endedPost) => () => {
    /*
    beforeStart: before start
    ends: after start before end (during)
    ended: after end


     */
    let started = false
    let finished = false
    let tillStart = Math.floor((start - Date.now()) / 1000)
    let tillEnd = Math.floor((end - Date.now()) / 1000);
    //console.log("Initial display:", display);
    if (tillStart < 0) { // has started
        started = true
    }
    if (tillEnd < 0) { // has ended
        finished = true
    }
    let display = started ? tillEnd : tillStart
    if (display < 0 && finished) {
        display = Math.abs(display)
    }
  /*console.log("End:", end);
  console.log("Start:", start);
  console.log("Now:", Date.now());
  console.log("d:", d);*/
    const day = Math.floor(display / 86400)
    const hour = Math.floor((display - day * 86400) / 3600)
    const minute = Math.floor((display - day * 86400 - hour * 3600) / 60)
    const second = display % 60
    let s = ''
    if (day === 1) {
        s += '1 day, '
    } else if (day === 0) {
    } else {
        s += `${day} days, `
    }
    s += ('0' + hour).slice(-2) + ':'
    s += ('0' + minute).slice(-2) + ':'
    s += ('0' + second).slice(-2)
    countdown.innerText = s
    if (display > 0) { // before the end
        updateColours(countdown.classList, "ending-5m", display < 60 * 5 && display >= 60)
        updateColours(countdown.classList, "ending-1m", display < 60 && display >= 10)
        updateColours(countdown.classList, "ending-10s", display < 10)
    }
    // TODO: js i18n
    eTextPre.innerText = started ? (finished ? endedPre : sanitizeEnd(endsPre)) : sanitizeStart(beforeStartPre)
    eTextPost.innerText = started ? (finished ? endedPost : sanitizeEnd(endsPost)) : sanitizeStart(beforeStartPost)
}

export default newCalculateTime
