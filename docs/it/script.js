function loadPage(path){
  document.getElementById('frame').src = path;
}
function filterTree(el){
  let term = el.value.toLowerCase();
  document.querySelectorAll('#sidebar ul.tree li').forEach(li=>{
    li.style.display = li.textContent.toLowerCase().includes(term) ? 'block' : 'none';
  });
}
