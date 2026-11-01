(function () {
  'use strict';
  const C = window.CapPro;
  const KEY = 'cap-pro.records.v1';
  const MODE_KEY = 'cap-pro.mode.v1';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const palette = [['#edf0e7','#7f8f66'],['#edf1fa','#6c84b1'],['#f8eee7','#bd916c'],['#f1ecf7','#9981af'],['#e7f1e9','#709675']];
  const statusTheme = {draft:['#f1f2f5','#dfe2e8','#5f6675'],sent:['#edf3fb','#d9e6f6','#3b6598'],followed:['#fbf3e5','#efdfbf','#8a672d'],interview:['#edf6ec','#d8e9d2','#426a37'],offer:['#f3edf8','#e5d7ef','#77508f'],closed:['#f1f3ef','#e1e5dc','#67785d']};
  const state = {personal: [], demo: C.demoRecords(), mode: 'demo', nav: 'all', query: '', status: '', sort: 'recent', view: 'list', canWrite: true};
  let toastTimer;
  function warning(message) { $('storageWarning').textContent = message; $('storageWarning').hidden = false; }
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const payload = JSON.parse(raw);
      if (payload.version !== 1 || !Array.isArray(payload.records)) throw new Error('format');
      state.personal = payload.records.map(C.normalize);
      if (new Set(state.personal.map(record => record.id)).size !== state.personal.length) throw new Error('duplicate IDs');
    }
    const savedMode = localStorage.getItem(MODE_KEY);
    state.mode = savedMode === 'personal' || (!savedMode && state.personal.length) ? 'personal' : 'demo';
  } catch (_) {
    state.canWrite = false;
    warning('Le stockage de ce navigateur est indisponible ou ses données sont illisibles. Les données existantes ne seront pas écrasées. Vos nouvelles saisies restent temporaires : exportez-les avant de quitter cette page.');
  }
  function records() { return state[state.mode === 'demo' ? 'demo' : 'personal']; }
  function save() {
    if (!state.canWrite) return false;
    try { localStorage.setItem(KEY, JSON.stringify({version:1,records:state.personal})); return true; }
    catch (_) { state.canWrite=false; warning('La sauvegarde locale a échoué. Gardez une copie de vos données avec Exporter CSV avant de quitter cette page.'); return false; }
  }
  function saveMode() { try { localStorage.setItem(MODE_KEY, state.mode); } catch (_) {} }
  function toast(message) { clearTimeout(toastTimer); $('toast').textContent = message; $('toast').hidden = false; toastTimer = setTimeout(() => { $('toast').hidden = true; }, 4200); }
  function dateParts(value) { const [year,month,day] = value.split('-').map(Number); return new Date(year,month-1,day); }
  function formatDate(value, full = false) { return value ? dateParts(value).toLocaleDateString('fr-FR', {day:'numeric',month:full?'long':'short', ...(full ? {year:'numeric'} : {})}) : 'Non planifiée'; }
  function shortName(company) { const n = [...company].reduce((sum,c) => sum + c.charCodeAt(0),0); const [bg,ink] = palette[n % palette.length]; return `<span class="company-monogram" style="--company-bg:${bg};--company-ink:${ink}" aria-hidden="true">${esc(company.slice(0,1).toLocaleUpperCase('fr'))}</span>`; }
  function companyLabel(record) { return record.url ? `<a href="${esc(record.url)}" target="_blank" rel="noopener noreferrer" title="Voir l’offre (nouvel onglet)">${esc(record.company)} <span aria-hidden="true">↗</span></a>` : esc(record.company); }
  function options(value) { return C.STATUSES.map(status => `<option value="${status.id}"${status.id === value ? ' selected' : ''}>${status.label}</option>`).join(''); }
  function statusControl(record) {
    const [bg,border,text] = statusTheme[record.status];
    const style = `--status-bg:${bg};--status-border:${border};--status-text:${text}`;
    return `<div class="status-control" style="${style}">${record.deletedAt ? `<span class="status-pill">${C.STATUSES.find(s=>s.id===record.status).label}</span>` : `<select class="status-select" data-status="${esc(record.id)}" aria-label="Statut de la candidature chez ${esc(record.company)}">${options(record.status)}</select>`}</div>`;
  }
  function followup(record) {
    const due = C.due(record);
    const caption = record.followUp ? (record.followUp === C.isoDate() ? 'Aujourd’hui' : formatDate(record.followUp)) : 'Non planifiée';
    return `<div class="followup${due ? ' overdue' : ''}"><strong>${esc(caption)}</strong><small>${due ? 'Relance à prévoir' : record.followUp && !C.isTerminal(record) ? 'Prochaine relance' : 'Date de suivi'}</small></div>`;
  }
  function actions(record) { return `<div class="record-actions">${record.deletedAt ? `<button class="icon-button restore" data-restore="${esc(record.id)}" aria-label="Restaurer la candidature chez ${esc(record.company)}">↶ Restaurer</button>` : `<button class="icon-button" data-edit="${esc(record.id)}" aria-label="Modifier la candidature chez ${esc(record.company)}" title="Modifier">✎</button><button class="icon-button delete-button" data-trash="${esc(record.id)}" aria-label="Déplacer la candidature chez ${esc(record.company)} dans la corbeille" title="Déplacer dans la corbeille">♲</button>`}</div>`; }
  function renderStats() {
    const m = C.metrics(records());
    const data = [
      ['Candidatures',m.total,'Votre parcours de recherche','▦','#edf2eb','#8fa27b'],
      ['En cours',m.pending,'Envoyées, relancées ou en entretien','↗','#eef3fb','#7d9cbd'],
      ['Entretiens',m.interviews,'De nouvelles conversations','◇','#f9eee5','#c69a74'],
      ['À relancer',m.due,'Aujourd’hui ou en retard','◷','#f2eef9','#ab94c3'],
    ];
    $('stats').innerHTML = data.map(([label,count,caption,icon,tint,tone])=>`<article class="stat-card" style="--tint:${tint};--tone:${tone}"><div class="stat-top"><p>${label}</p><span class="stat-icon" aria-hidden="true">${icon}</span></div><p class="stat-number">${count}</p><span class="stat-caption">${caption}</span></article>`).join('');
    $('allCount').textContent=m.total; $('dueCount').textContent=m.due; $('interviewCount').textContent=m.interviews; $('trashCount').textContent=m.trash;
    const live = records().filter(record=>!record.deletedAt);
    const stages = C.STATUSES.map(status=>({...status,count:live.filter(record=>record.status===status.id).length}));
    $('distribution').innerHTML = stages.filter(stage=>stage.count).map(stage=>`<i style="flex:${stage.count};background:${stage.color}"></i>`).join('');
    $('stageLegend').innerHTML = stages.map(stage=>`<div class="legend-item"><i style="--dot:${stage.color}" aria-hidden="true"></i>${stage.label}<b>${stage.count}</b></div>`).join('');
    const next = live.filter(record=>record.followUp && record.status!=='draft' && !C.isTerminal(record)).sort((a,b)=>a.followUp.localeCompare(b.followUp))[0];
    if (next) {
      const date=dateParts(next.followUp);
      $('nextPanel').innerHTML=`<div class="next-label"><span></span>${C.due(next)?'UNE RELANCE À PRÉVOIR':'VOTRE PROCHAINE RELANCE'}</div><div class="next-content"><div class="calendar-badge"><small>${esc(date.toLocaleDateString('fr-FR',{month:'short'}).toLocaleUpperCase('fr'))}</small><b>${date.getDate()}</b></div><div><h3>${esc(next.company)}</h3><p>${esc(next.role)}</p></div></div><button class="link-button" data-edit="${esc(next.id)}">Préparer la suite ↗</button>`;
    } else $('nextPanel').innerHTML='<div class="next-label"><span></span>GARDER UNE LONGUEUR D’AVANCE</div><div class="next-empty"><h3>Un peu de place pour la suite.</h3><p>Ajoutez une date de relance à une candidature envoyée pour retrouver ici votre prochaine étape.</p></div>';
  }
  function emptyState(items) {
    if (items.length) return false;
    const filtered = !!(state.query || state.status);
    const headline = filtered ? 'Aucun résultat pour cette recherche.' : state.nav === 'trash' ? 'La corbeille est vide.' : state.nav === 'due' ? 'Vous êtes à jour.' : state.nav === 'interview' ? 'Les prochains échanges arrivent.' : 'Votre prochaine étape commence ici.';
    const message = filtered ? 'Essayez un autre mot-clé ou retirez les filtres.' : state.nav === 'trash' ? 'Les candidatures retirées restent ici et peuvent être restaurées.' : state.nav === 'due' ? 'Aucune relance à prévoir aujourd’hui. Les suivis à venir restent visibles dans la vue d’ensemble.' : state.nav === 'interview' ? 'Passez une candidature au statut Entretien pour la retrouver ici.' : 'Ajoutez votre première candidature. Son suivi restera enregistré dans ce navigateur.';
    $('records').innerHTML=`<div class="empty-state"><span class="empty-symbol" aria-hidden="true">${state.nav==='due'?'✓':'↗'}</span><h3>${headline}</h3><p>${message}</p>${filtered ? '<button class="button secondary" data-clear>Réinitialiser les filtres</button>' : state.nav==='all' ? '<button class="button primary" data-new>Ajouter ma première candidature</button>' : '<button class="button secondary" data-nav="all">Vue d’ensemble</button>'}</div>`;
    return true;
  }
  function renderRecords() {
    const items=C.visible(records(),state);
    const titles={all:'Toutes les candidatures',due:'À relancer',interview:'Entretiens',trash:'Corbeille'};
    $('listTitle').firstChild.textContent=titles[state.nav]+' ';
    $('listCount').textContent=items.length;
    $('resultSummary').textContent=`${items.length} candidature${items.length!==1?'s':''} affichée${items.length!==1?'s':''}${state.mode==='demo'?' · Exemples fictifs':''}.`;
    $('exportButton').disabled=!items.length;
    $('boardView').disabled=state.nav==='trash';
    $('listView').setAttribute('aria-pressed',String(state.view==='list'||state.nav==='trash'));
    $('boardView').setAttribute('aria-pressed',String(state.view==='board'&&state.nav!=='trash'));
    if(emptyState(items))return;
    if(state.view==='board'&&state.nav!=='trash'){
      $('records').innerHTML='<div class="board" role="region" aria-label="Tableau des candidatures, défilement horizontal" tabindex="0">'+C.STATUSES.map(status=>{
        const group=items.filter(record=>record.status===status.id);
        return `<section class="board-column" aria-label="${status.label}"><h3>${status.label}<span>${group.length}</span></h3>${group.map(record=>`<article class="board-card">${shortName(record.company)}<h4>${companyLabel(record)}</h4><p>${esc(record.role)}</p>${statusControl(record)}${followup(record)}${actions(record)}</article>`).join('')||'<p class="board-empty">Aucune candidature à cette étape.</p>'}</section>`;
      }).join('')+'</div>';
    }else $('records').innerHTML='<div class="list-labels" aria-hidden="true"><span>ENTREPRISE & POSTE</span><span>STATUT</span><span>PROCHAIN SUIVI</span><span>ACTIONS</span></div>'+items.map(record=>`<article class="record-row"><div class="company-info">${shortName(record.company)}<div><h3>${companyLabel(record)}</h3><p>${esc(record.role)}</p></div></div>${statusControl(record)}${followup(record)}${actions(record)}</article>`).join('');
  }
  function render() {
    const demo=state.mode==='demo';
    $('demoMode').setAttribute('aria-pressed',String(demo)); $('personalMode').setAttribute('aria-pressed',String(!demo));
    $('demoBanner').hidden=!demo;
    $('saveState').innerHTML='<i aria-hidden="true"></i>'+(demo?'Démo · Modifications temporaires':state.canWrite?'Enregistré sur cet appareil':'Mode temporaire · Export conseillé');
    document.querySelectorAll('.side-nav [data-nav]').forEach(button=>{const active=button.dataset.nav===state.nav;button.classList.toggle('active',active);if(active)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});
    renderStats(); renderRecords();
  }
  function resetFilters() { state.query='';state.status='';$('searchInput').value='';$('statusFilter').value=''; }
  function switchMode(mode) { state.mode=mode;state.nav='all';resetFilters();saveMode();render(); }
  function openForm(id) {
    const record=id?records().find(item=>item.id===id):null;
    if(id&&!record)return;
    $('applicationForm').reset(); $('formError').hidden=true;
    $('recordId').value=record?.id||'';
    $('applicationForm').dataset.mode=record?state.mode:'personal';
    $('dialogTitle').textContent=record?(state.mode==='demo'?'Modifier un exemple':'Modifier la candidature'):'Nouvelle candidature';
    $('dialogNote').textContent=record&&state.mode==='demo'?'Vous modifiez un exemple fictif. Les changements de la démo disparaissent au rechargement.':'Cette candidature sera enregistrée dans votre espace personnel, sur cet appareil.';
    $('companyField').value=record?.company||''; $('roleField').value=record?.role||''; $('statusField').value=record?.status||'sent'; $('appliedField').value=record?.appliedDate||C.isoDate(); $('followupField').value=record?.followUp||''; $('urlField').value=record?.url||''; $('notesField').value=record?.notes||'';
    $('applicationDialog').showModal(); $('companyField').focus();
  }
  function updateRecord(id, changes) {
    const list=records(); const index=list.findIndex(record=>record.id===id); if(index<0)return;
    list[index]=C.normalize({...list[index],...changes});
    const stored=state.mode==='personal'?save():true;
    render(); return stored;
  }
  $('statusFilter').insertAdjacentHTML('beforeend',options(''));
  $('statusField').innerHTML=options('sent');
  $('demoMode').addEventListener('click',()=>switchMode('demo'));
  $('personalMode').addEventListener('click',()=>switchMode('personal'));
  $('startPersonal').addEventListener('click',()=>switchMode('personal'));
  $('addButton').addEventListener('click',()=>openForm());
  ['closeDialog','cancelDialog'].forEach(id=>$(id).addEventListener('click',()=>$('applicationDialog').close()));
  $('searchInput').addEventListener('input',event=>{state.query=event.target.value;renderRecords();});
  $('statusFilter').addEventListener('change',event=>{state.status=event.target.value;renderRecords();});
  $('sortSelect').addEventListener('change',event=>{state.sort=event.target.value;renderRecords();});
  $('listView').addEventListener('click',()=>{state.view='list';renderRecords();});
  $('boardView').addEventListener('click',()=>{state.view='board';renderRecords();});
  document.addEventListener('click',event=>{
    const button=event.target.closest('button'); if(!button)return;
    if(button.dataset.nav){state.nav=button.dataset.nav;resetFilters();render();}
    else if(button.hasAttribute('data-new'))openForm();
    else if(button.hasAttribute('data-clear')){resetFilters();renderRecords();$('searchInput').focus();}
    else if(button.dataset.edit)openForm(button.dataset.edit);
    else if(button.dataset.trash){updateRecord(button.dataset.trash,{deletedAt:C.isoDate()});toast('Candidature déplacée dans la corbeille. Vous pouvez la restaurer.');}
    else if(button.dataset.restore){updateRecord(button.dataset.restore,{deletedAt:null});toast('Candidature restaurée dans votre liste.');}
  });
  $('records').addEventListener('change',event=>{
    const id=event.target.dataset.status; if(!id)return;
    updateRecord(id,{status:event.target.value});
    [...$('records').querySelectorAll('[data-status]')].find(select=>select.dataset.status===id)?.focus();
    toast(state.mode==='demo'?'Statut de l’exemple mis à jour.':'Statut mis à jour.');
  });
  $('applicationForm').addEventListener('submit',event=>{
    event.preventDefault();
    const existingId=$('recordId').value;
    const mode=$('applicationForm').dataset.mode;
    const list=state[mode==='demo'?'demo':'personal'];
    const existing=list.find(record=>record.id===existingId);
    try{
      const record=C.normalize({id:existingId||(window.crypto?.randomUUID?.()||`record-${Date.now()}-${Math.random().toString(36).slice(2)}`),company:$('companyField').value,role:$('roleField').value,status:$('statusField').value,appliedDate:$('appliedField').value,followUp:$('followupField').value,url:$('urlField').value,notes:$('notesField').value,deletedAt:existing?.deletedAt||null});
      const index=list.findIndex(item=>item.id===record.id); if(index<0)list.unshift(record);else list[index]=record;
      state.mode=mode; if(!existingId){state.nav='all';resetFilters();}
      const stored=mode==='personal'?save():true;
      saveMode(); $('applicationDialog').close(); render();
      toast(!stored?'Candidature ajoutée pour cette session. Pensez à exporter votre liste.':existingId?'Candidature mise à jour.':'Candidature ajoutée à votre espace personnel.');
      [...$('records').querySelectorAll('[data-edit]')].find(button=>button.dataset.edit===record.id)?.focus();
    }catch(error){$('formError').textContent=error.message;$('formError').hidden=false;}
  });
  $('exportButton').addEventListener('click',()=>{
    const items=C.visible(records(),state);if(!items.length)return;
    const blob=new Blob([C.toCSV(items)],{type:'text/csv;charset=utf-8;'});const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=`cap-pro-${state.mode==='demo'?'demo-':''}${C.isoDate()}.csv`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);toast(`Export CSV préparé : ${items.length} candidature${items.length>1?'s':''}.`);
  });
  render();
})();
