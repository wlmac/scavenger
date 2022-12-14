const e = document.getElementById("countdown")
const eText = document.getElementById("countdown-text")

function assertClass(classList, className, contains) {
  if (contains) {
    if (!classList.contains(className)) classList.add(className)
  } else {
    if (classList.contains(className)) classList.remove(className)
  }
}

const newCalculateTime = (start, end, starts, ends, ended) => () => {
  let started = false
  let finished = false
  let d = Math.floor((end - Date.now()) / 1000)
  //console.log("Initial d:", d);
  if (d < 0) {
    d = Math.floor((start - Date.now()) / 1000);
    finished = d < 0
    started = true
  }

  /*console.log("End:", end);
  console.log("Start:", start);
  console.log("Now:", Date.now());
  console.log("d:", d);*/
  const day = Math.floor(d / 86400)
  const hour = Math.floor((d - day * 86400) / 3600)
  const minute = Math.floor((d - day * 86400 - hour * 3600) / 60)
  const second = d % 60
  let s = ''
  if (day == 1) s += '1 day, '
  else if (day == 0) {}
  else {
    s += `${day} days, `
  }
  s += ('0' + hour).slice(-2) + ':'
  s += ('0' + minute).slice(-2) + ':'
  s += ('0' + second).slice(-2)
  e.innerText = s
  if (d > 0) {
    assertClass(e.classList, "soon-very1", d < 60*5 && d >= 60)
    assertClass(e.classList, "soon-very2", d < 60 && d >= 10)
    assertClass(e.classList, "soon-very3", d < 10)
  }
  eText.innerText = started ? (finished ? ended : ends) : starts
}

export default newCalculateTime
