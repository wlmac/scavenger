const btn = document.getElementById('share-btn')
const link = window.location.origin + btn.dataset.joinLink
if (navigator.share) {
  console.log('share api avail')
  btn.value = btn.dataset.shareText
}
btn.addEventListener('click', async (e) => {
  await ((navigator.share) ? navigator.share(link) : await navigator.clipboard.writeText(link))
})

new QRCode(document.getElementById("qrcode"), {
  text: link,
  correctLevel: QRCode.CorrectLevel.H,
})
