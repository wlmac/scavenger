const btn = document.getElementById('share-btn')
if (navigator.share) {
  console.log('share api avail')
  btn.value = btn.dataset.shareText
}
btn.addEventListener('click', async (e) => {
  await ((navigator.share) ? navigator.share(btn.dataset.joinLink) : await navigator.clipboard.writeText(btn.dataset.joinLink))
})

new QRCode(document.getElementById("qrcode"), {
  text: window.location.origin + btn.dataset.joinLink,
  correctLevel: QRCode.CorrectLevel.H,
})
