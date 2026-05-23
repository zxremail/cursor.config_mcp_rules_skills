(function(){
  mermaid.initialize({
    startOnLoad:false,
    theme:'dark',
    themeVariables:{
      darkMode:true,
      background:'#0d1117',
      primaryColor:'#21262d',
      primaryBorderColor:'#30363d',
      primaryTextColor:'#c9d1d9',
      lineColor:'#8b949e',
      secondaryColor:'#1a1428',
      tertiaryColor:'#0d2137'
    },
    flowchart:{htmlLabels:true,curve:'basis'},
    sequence:{actorMargin:50,messageFontSize:13}
  });

  const mdSrc = document.getElementById('md-source').textContent;

  const renderer = new marked.Renderer();
  const origCode = renderer.code.bind(renderer);
  renderer.code = function(code, lang){
    if(lang && lang.startsWith('customfig:')){
      const id = lang.slice('customfig:'.length).trim();
      const tpl = document.getElementById(id);
      if(tpl) return tpl.innerHTML;
      return '<div class="missing-figure">缺少自绘图模板: <code>'+id+'</code></div>';
    }
    if(lang === 'mermaid'){
      return '<div class="mermaid">'+code+'</div>';
    }
    return origCode(code, lang);
  };

  var __hIdx = 0;
  renderer.heading = function(text, level){
    var plain = String(text).replace(/<[^>]*>/g,'').trim();
    var m = /^(\d+(?:\.\d+)*)/.exec(plain);
    var id;
    if(m){ id = 'h-'+m[1].replace(/\./g,'-'); }
    else {
      var ap = /^附录\s*([A-Z])/i.exec(plain);
      id = ap ? 'h-appendix-'+ap[1].toLowerCase() : 'h-misc-'+(++__hIdx);
    }
    return '<h'+level+' id="'+id+'">'+text+'</h'+level+'>\n';
  };

  marked.setOptions({renderer:renderer, gfm:true, breaks:false});
  document.getElementById('content').innerHTML = marked.parse(mdSrc);

  const toc = document.getElementById('toc');
  let _idx = 0;
  document.querySelectorAll('#content h2, #content h3').forEach(function(h){
    if(h.closest('.customfig')) return;
    if(!h.id){
      var m = /^(\d+(?:\.\d+)*)/.exec(h.textContent.trim());
      h.id = m ? 'h-'+m[1].replace(/\./g,'-') : 'h-'+(++_idx);
    }
    var txt = h.textContent.trim();
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = '#'+h.id;
    a.textContent = txt;
    if(h.tagName === 'H3') a.className = 'sub';
    a.addEventListener('click', function(e){
      e.preventDefault();
      h.scrollIntoView({behavior:'smooth', block:'start'});
    });
    li.appendChild(a);
    toc.appendChild(li);
  });

  document.getElementById('content').addEventListener('click', function(e){
    var a = e.target.closest('a[href^="#"]');
    if(!a) return;
    e.preventDefault();
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    var target = document.getElementById(id);
    if(target) target.scrollIntoView({behavior:'smooth', block:'start'});
  });

  mermaid.run({querySelector:'.mermaid'}).catch(function(err){
    console.warn('mermaid render:', err);
  });
})();
