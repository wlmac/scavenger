const btn = document.getElementById('share-btn')
const link = window.location.origin + btn.dataset.joinLink
 const shareData = {
  title: 'MacLyonsDen Scavenger Hunt',
  text: 'Scavenger hunt team invite code!',
  url: link
};

btn.addEventListener('click',  (e) => {
   ((navigator.share) ? navigator.share(shareData) : navigator.clipboard.writeText(link))
})

new QRCode(document.getElementById("qrcode"), {
  text: link,
  correctLevel: QRCode.CorrectLevel.H,
})
