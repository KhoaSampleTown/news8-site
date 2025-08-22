async function j(path){ const r = await fetch(path); return r.json(); }
function htm([s,...r],...v){ return v.reduce((a,b,i)=>a+b+r[i], s); }

async function main(){
  const idx = await j('/data/latest.json');
  document.getElementById('date').textContent = `Edition: ${idx.date}`;

  // Summaries
  const summariesSec = document.getElementById('summaries');
  if (idx.summaries){
    const sum = await j(idx.summaries.path);
    const order = ["fixedincome","equity","commodity","cryptocurrency","exchangerate","interestrate"];
    for (const t of order){
      const sec = sum.sections?.[t];
      if (!sec) continue;
      const wrap = document.createElement('section');
      wrap.className = 'topic';
      const bullets = (sec.bullets||[]).map(b=>`<li>${b}</li>`).join('');
      wrap.innerHTML = htm`<h2>${t}</h2>
        <article class="card">
          <ul class="bullets">${bullets}</ul>
          <p><em>${sec.takeaway||''}</em></p>
        </article>`;
      summariesSec.appendChild(wrap);
    }
  }

  // Raw items
  const topicsSec = document.getElementById('topics');
  for (const [topic, meta] of Object.entries(idx.topics)){
    const data = await j(meta.path);
    const sec = document.createElement('section');
    sec.className = 'topic';
    sec.innerHTML = `<h2>${topic}</h2><div class="grid"></div>`;
    const grid = sec.querySelector('.grid');

    for (const it of data.items){
      const el = document.createElement('article');
      el.className = 'card';
      let host='';
      try{ host = new URL(it.link).hostname }catch{}
      el.innerHTML = `
        <div class="title"><a href="${it.link}" target="_blank" rel="noopener">${it.title}</a></div>
        <div class="meta">${(it.published||'').replace('T',' ').slice(0,16)} · ${host}</div>
        <p>${it.summary||''}</p>`;
      grid.appendChild(el);
    }
    topicsSec.appendChild(sec);
  }
}
main();
