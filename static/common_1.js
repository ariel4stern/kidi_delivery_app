const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function api(u,body,method){
  const o={method:method||(body!==undefined?'POST':'GET'),headers:{}};
  if(body!==undefined){o.headers['Content-Type']='application/json';o.body=JSON.stringify(body)}
  const r=await fetch(u,o);let d={};try{d=await r.json()}catch(e){}
  if(!r.ok||d.ok===false){let t=d.detail;if(t&&typeof t!=='string')t=JSON.stringify(t);throw new Error(t||r.statusText)}
  return d}
function say(el,t,ok){el.className='msg '+(ok?'ok':'err');el.textContent=t;el.hidden=false}
const cell=v=>v&&typeof v==='object'?JSON.stringify(v):v;
function table(rows){if(!rows||!rows.length)return'<p>No rows.</p>';const k=Object.keys(rows[0]);
  return'<div class="tw"><table><tr>'+k.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr>'+
  rows.map(r=>'<tr>'+k.map(x=>'<td>'+esc(cell(r[x]))+'</td>').join('')+'</tr>').join('')+'</table></div>'}
function render(x){
  if(Array.isArray(x))return x.length&&typeof x[0]==='object'?table(x):'<p>'+esc(JSON.stringify(x))+'</p>';
  if(x&&typeof x==='object'){let h='',m=[];
    for(const[k,v]of Object.entries(x)){
      if(Array.isArray(v)&&v.length&&typeof v[0]==='object')h+='<h4>'+esc(k)+'</h4>'+table(v);
      else if(v&&typeof v==='object')h+='<h4>'+esc(k)+'</h4>'+table([v]);else m.push(k+': '+v)}
    return(m.length?'<p><b>'+esc(m.join(' | '))+'</b></p>':'')+h}
  return'<p>'+esc(x)+'</p>'}
function modal(title,html,onOk){
  const ov=document.createElement('div');ov.className='ov';
  ov.innerHTML='<div class="box"><h3>'+esc(title)+'</h3><div class="mb">'+html+'</div><div class="msg" hidden></div><div class="row"><button class="go">Confirm</button><button class="x">Close</button></div></div>';
  document.body.appendChild(ov);const box=$('.box',ov),m=$('.msg',ov);
  $('.x',ov).onclick=()=>ov.remove();
  $('.go',ov).onclick=async()=>{try{say(m,await onOk(box),true)}catch(e){say(m,e.message,false)}};
  return box}
function sky(){const s=$('#sky');if(!s)return;
  for(let i=0;i<40;i++){const d=document.createElement('i');d.className='dot';const z=2+Math.random()*5;
    d.style.cssText=`left:${Math.random()*100}%;width:${z}px;height:${z}px;--dx:${Math.random()*120-60}px;animation-duration:${12+Math.random()*20}s;animation-delay:-${Math.random()*30}s`;s.appendChild(d)}}

/* ---------- toolbar ---------- */
function toolbar(){
  const b=id=>$('#'+id);if(!b('btnAvail'))return;
  b('btnAvail').onclick=async()=>{
    const d=(await api('/api/drivers/status')).drivers;
    modal('Set drivers to available',d.map(x=>`<label><input type="checkbox" value="${x.driver_id}">${esc(x.driver_name)} (id ${x.driver_id}) - ${esc(x.driver_status)}</label>`).join(''),
      async box=>{const ids=$$('input:checked',box).map(i=>+i.value);if(!ids.length)throw new Error('Choose at least one driver.');
        return(await api('/api/drivers/set_available',{driver_ids:ids})).detail})};
  b('btnPoint').onclick=async()=>{
    const [p,d]=await Promise.all([api('/api/points/today'),api('/api/drivers/names')]);
    modal('Change driver of a point ('+p.day+')',
      '<h4>Point</h4>'+p.points.map(x=>`<label><input type="radio" name="pt" value="${x.point}">Point ${x.point} - now ${esc(x.driver_name)}</label>`).join('')+
      '<h4>New driver</h4>'+d.drivers.map(x=>`<label><input type="radio" name="dr" value="${x.driver_id}">${esc(x.driver_name)} (id ${x.driver_id})</label>`).join(''),
      async box=>{const pt=$('[name=pt]:checked',box),dr=$('[name=dr]:checked',box);
        if(!pt||!dr)throw new Error('Choose one point and one driver.');
        return(await api('/api/points/change_driver',{point:+pt.value,driver_id:+dr.value})).detail})};
  b('btnMaint').onclick=()=>modal('Maintenance',
    '<label><input type="radio" name="mt" value="1">Reset all drivers cartoons count to 0</label><label><input type="radio" name="mt" value="2">Refresh output_data_two</label><label><input type="radio" name="mt" value="3">Refresh output_data</label>',
    async box=>{const v=($('[name=mt]:checked',box)||{}).value;if(!v)throw new Error('Choose one option.');
      if(v==='1')return(await api('/api/maintenance/reset_counts',{})).detail;
      if(v==='2')return(await api('/api/maintenance/refresh_output_two',{})).detail;
      await api('/api/manage/e_router_output_table.py/refresh_output_table_data',{});return'output_data was refreshed.'})}

/* ---------- tab 1 ---------- */
let locked=false;
async function loadRows(){
  const t=$('#cntBody');if(!t)return;
  const rows=(await api('/api/rows')).rows;
  t.innerHTML=rows.map(r=>`<tr data-n="${r.store_number}"><td>${r.store_number}</td><td><input type="number" min="0" class="c"></td><td><input type="number" min="0" class="g"></td></tr>`).join('')||'<tr><td colspan=3>No stores today.</td></tr>';
  $$('#cntBody input').forEach(i=>i.oninput=check);check()}
const empty=()=>$$('#cntBody input').filter(i=>i.value==='');
function check(){const b=$('#btnFinish');if(b)b.classList.toggle('off',locked||empty().length>0)}
async function finish(){
  const m=$('#cntMsg'),e=empty();
  if(e.length){e.forEach(i=>i.classList.add('bad'));e[0].scrollIntoView({block:'center'});e[0].focus();
    return say(m,'You must fill all cells. If no cartoons left, fill with 0.',false)}
  const rows=$$('#cntBody tr[data-n]').map(tr=>({store_number:+tr.dataset.n,cartoons:+$('.c',tr).value,bags:+$('.g',tr).value}));
  try{await api('/api/counting/finish',{rows});locked=true;$$('#cntBody input').forEach(i=>i.disabled=true);check();
    say(m,'Success You allow to move on',true);loadOut()}
  catch(x){say(m,x.message,false)}}

/* ---------- tab 2 ---------- */
async function loadOut(){const o=$('#outTable');if(!o)return;
  try{o.innerHTML=table((await api('/api/output')).rows)}catch(e){say($('#outMsg'),e.message,false)}}
async function download(){const m=$('#outMsg');
  try{const r=await fetch('/api/export');if(!r.ok)throw new Error((await r.json()).detail||r.statusText);
    const a=document.createElement('a');a.href=URL.createObjectURL(await r.blob());
    a.download=(r.headers.get('content-disposition')||'').match(/filename="?([^";]+)/)?.[1]||'distribution_report.xlsx';a.click();say(m,'Excel file downloaded.',true)}
  catch(e){say(m,e.message,false)}}

/* ---------- tab 3 ---------- */
let REG={};
async function loadMerged(){const o=$('#mrgTable');if(o)try{o.innerHTML=table((await api('/api/merged')).rows)}catch(e){o.textContent=e.message}}
async function initDb(){
  const rs=$('#rSel');if(!rs)return;REG=await api('/api/manage/registry');
  rs.innerHTML=Object.keys(REG).map(k=>`<option>${k}</option>`).join('');
  const fn=()=>{const f=$('#fSel');f.innerHTML=Object.keys(REG[rs.value]).filter(x=>x!=='patch_output_two_data').map(k=>`<option>${k}</option>`).join('');tpl()};
  const tpl=()=>{const t=REG[rs.value][$('#fSel').value]||{};$('#jIn').value=Object.keys(t).length?JSON.stringify(t,null,2):'';$('#jIn').hidden=!Object.keys(t).length};
  rs.onchange=fn;$('#fSel').onchange=tpl;fn();
  const run=async(router,func,txt,msg,out)=>{
    try{const body=txt.trim()?JSON.parse(txt):{};const r=await api(`/api/manage/${router}/${func}`,body);
      say(msg,'Success: '+func+' completed.',true);if(out)out.innerHTML=render(r.result)}
    catch(e){say(msg,e.message,false);if(out)out.innerHTML=''}};
  $('#runBtn').onclick=()=>run(rs.value,$('#fSel').value,$('#jIn').value,$('#runMsg'),$('#runOut'));
  const t2=REG['eb_router_output_table_two.py'].patch_output_two_data;$('#p2In').value=JSON.stringify(t2,null,2);
  $('#p2Btn').onclick=async()=>{await run('eb_router_output_table_two.py','patch_output_two_data',$('#p2In').value,$('#p2Msg'));loadMerged()};
  loadMerged()}

document.addEventListener('DOMContentLoaded',()=>{
  sky();toolbar();$('#btnFinish')&&($('#btnFinish').onclick=finish);
  $('#btnDl')&&($('#btnDl').onclick=download);$('#btnRef')&&($('#btnRef').onclick=loadOut);
  loadRows().catch(()=>{});loadOut();initDb().catch(()=>{})});
