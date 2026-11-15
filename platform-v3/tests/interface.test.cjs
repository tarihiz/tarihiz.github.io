const test=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');

// Exercise the click handlers and rendered content independently of network access.
test('Konu seçimi, kaynak, bekleme göstergesi ve sohbet konumunun korunması',async()=>{
  const elements=new Map();
  function element(key) {
    if(!elements.has(key)) elements.set(key,{dataset:{},scrollTop:0,classList:{toggle(){},remove(){}},
      focus(){},querySelectorAll(){return [];},setAttribute(){},removeAttribute(){}});
    return elements.get(key);
  }
  const topicButton=element('topic');topicButton.dataset.topic='B';
  const askButton=element('ask');askButton.dataset.action='ask';
  const work={id:'w',topic_id:'B',revision:1,activity_snapshot:{id:'B',title:'Esnaf',question:'Mektup ne anlatır?',demo:true,sources:[{title:'Mektup',text:'Kurmaca belge'}]},state:{stage:'chat',messages:[]}};
  let release;
  const context={document:{querySelector:element,querySelectorAll:q=>q==='[data-topic]'?[topicButton]:[askButton]},
    matchMedia:()=>({matches:true}),setInterval(){},clearTimeout,URL,window:{TARIHIZ_CONFIG:{apiBase:'https://test.invalid'}},
    async fetch(url,opts) {
      const input=JSON.parse(opts.body);
      if(url.endsWith('/anonymous-session')) return Response.json({token:'t',topics:[{title:'Esnaf',id:'B',stage:'chat'}]});
      if(url.endsWith('/works')) {assert.equal(input.topic_id,'B');return Response.json(work);}
      if(input.action==='reply') {work.state.messages.push({role:'student',text:input.text});return Response.json(work);}
      assert.equal(input.action,'ask');
      await new Promise(resolve=>release=resolve);
      work.state.messages.push({role:'assistant',feedback:'Bir fark belirttin.',text:'Hangi kanıt?'});return Response.json(work);
    }};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),context);
  const saved=new Map();
  context.localStorage={getItem:k=>saved.get(k),setItem:(k,v)=>saved.set(k,v)};
  context.crypto=require('node:crypto').webcrypto;
  await element('#start').onclick();
  await new Promise(setImmediate);
  assert.match(element('#screen').innerHTML,/Konu Başlıkları.*Devam Ediyor/s);
  await topicButton.onclick();
  assert.match(element('#screen').innerHTML,/Kurmaca belge/);
  assert.equal(element('#researchText').textContent,'Mektup ne anlatır?');
  element('#activityBody').dataset.stage='chat';element('#activityBody').scrollTop=120;element('#screen').scrollTop=75;
  const pending=askButton.onclick();await new Promise(setImmediate);
  assert.equal(element('#status').textContent,'Yanıtınız hazırlanıyor…');
  release();await pending;
  assert.match(element('#screen').innerHTML,/Hangi kanıt/);
  askButton.dataset.action='reply';element('#response').value='Fark var.';
  const follow=askButton.onclick();await new Promise(setImmediate);
  assert.equal(element('#status').textContent,'Yanıtınız hazırlanıyor…');
  release();await follow;
  assert.deepEqual(work.state.messages.map(m=>m.role),['assistant','student','assistant']);
  assert.match(element('#screen').innerHTML,/Bir fark belirttin/);
  assert.equal(element('#activityBody').scrollTop,120);assert.equal(element('#screen').scrollTop,75);
});

test('İki konu kartı farklı kayıt ve kaynak açar; anket tüm mevcut konulara bağlıdır',async()=>{
  const elements=new Map();
  function element(id) {
    if(!elements.has(id)) elements.set(id,{dataset:{},scrollTop:0,classList:{toggle(){},remove(){}},
      querySelectorAll(){return [];},setAttribute(){},removeAttribute(){}});
    return elements.get(id);
  }
  const rows=[{id:'A',title:'Kasabada pazar hayatı',source:'Bir yolcunun günlüğü',stage:'done'},
    {id:'B',title:'Esnafın gündelik yaşamı',source:'Bir esnafın mektubu',stage:'chat'}];
  const buttons=rows.map(row=>({dataset:{topic:row.id}}));
  let mismatch=false;
  const ctx={document:{querySelector:q=>q==="#response"?null:element(q),querySelectorAll:q=>q==='[data-topic]'?buttons:[]},
    matchMedia:()=>({matches:true}),setInterval(){},clearTimeout,URL,window:{TARIHIZ_CONFIG:{apiBase:'https://test.invalid',feedbackFormUrl:'https://forms.gle/example'}},
    fetch:async (url,options)=>{
      if(url.endsWith('/topics')) return Response.json(rows);
      const id=JSON.parse(options.body).topic_id;
      const row=rows.find(r=>r.id===(mismatch?'A':id));
      return Response.json({topic_id:row.id,activity_snapshot:{id:row.id,title:row.title,question:row.title+'?',sources:[{title:row.source}]},
        state:{stage:row.stage,messages:[],initial:{text:'ilk'},final:{text:'son'}}});
    }};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),ctx);
  ctx.showTopics(rows);
  await buttons[0].onclick();assert.match(element('#screen').innerHTML,/Bir yolcunun günlüğü/);
  assert.doesNotMatch(element('#screen').innerHTML,/Ankete Katıl/);
  await element('#topics').onclick();await buttons[1].onclick();
  assert.match(element('#screen').innerHTML,/Bir esnafın mektubu/);
  assert.equal(element('#researchText').textContent,'Esnafın gündelik yaşamı?');
  assert.match(element('#steps').innerHTML,/class="step active" aria-current="step"/);
  rows[1].stage='done';await element('#topics').onclick();
  assert.match(element('#screen').innerHTML,/Ankete Katıl/);
  assert.match(element('#screen').innerHTML,/Sorgulamayı Tamamladın/);
  element('#review').onclick();assert.doesNotMatch(element('#screen').innerHTML,/Ankete Katıl/);
  await buttons[1].onclick();assert.doesNotMatch(element('#screen').innerHTML,/Ankete Katıl/);
  rows.push({id:'C',title:'Yeni konu',stage:null});await element('#topics').onclick();
  assert.doesNotMatch(element('#screen').innerHTML,/Ankete Katıl/);
  assert.equal(ctx.survey([]),'');
  mismatch=true;await buttons[1].onclick();assert.match(element('#status').textContent,/eşleşmedi/);
});
test('Görsel onayı ve mobil sekmede taslağın korunması',()=>{
  const nodes=new Map();
  const element=q=>{if(!nodes.has(q))nodes.set(q,{dataset:{},value:'',classList:{toggle(){}},setAttribute(){}});return nodes.get(q);};
  const ctx={document:{querySelector:element,querySelectorAll:()=>[]},URL,window:{},matchMedia:()=>({matches:true}),setInterval(){}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),ctx);
  const [gold,map]=require('../pilot-konular-taslak.json').konular.map(t=>t.sources[0]);
  assert.doesNotMatch(ctx.sourceHTML({...gold,image_ready:false}),/<img|Haritadaki İşaretler/);
  assert.match(ctx.sourceHTML(map),/Haritadaki İşaretler/);
  assert.match(ctx.sourceHTML({...map,image_ready:true}),/data-enlarge/);
  element('#response').value='Yarım kalan yanıt';
  ctx.setPane('source');ctx.setPane('evaluation');
  assert.equal(element('#response').value,'Yarım kalan yanıt');
  assert.equal(element('.topic-work').dataset.pane,'evaluation');
});

test('Beş görsel arasında geçiş yanıtı ve sohbet konumunu korur',()=>{
  const nodes=new Map();
  const element=q=>{if(!nodes.has(q))nodes.set(q,{dataset:{},value:'',scrollTop:0,classList:{toggle(){}},setAttribute(){}});return nodes.get(q);};
  const buttons=Array.from({length:5},(_,i)=>({dataset:{sourceChoice:String(i)},setAttribute(k,v){this[k]=v;}}));
  const ctx={document:{querySelector:element,querySelectorAll:q=>q==='[data-source-choice]'?buttons:[]},URL,window:{},matchMedia:()=>({matches:true}),setInterval(){}};
  vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),ctx);
  ctx.activity=require('../pilot-konular-taslak.json').konular[2];
  vm.runInContext('work={activity_snapshot:activity};',ctx);
  assert.equal((ctx.sourceGallery(ctx.activity).match(/data-source-choice=/g)||[]).length,5);
  element('#response').value='Henüz göndermediğim yorum';element('#activityBody').scrollTop=123;
  ctx.bindSourceGallery();
  for(let i=0;i<5;i++) {
    buttons[i].onclick();
    assert.ok(element('#selectedSource').innerHTML.includes(ctx.activity.sources[i].image));
    assert.equal(buttons[i]['aria-pressed'],'true');
    assert.equal(element('#response').value,'Henüz göndermediğim yorum');
    assert.equal(element('#activityBody').scrollTop,123);
  }
  assert.ok(ctx.sourceGallery(ctx.activity).includes(ctx.activity.sources[4].image));
});

test('Rize metni ve ayrı künyesi görünür; başlıklar numaralanır',()=>{
 const nodes=new Map();const el=q=>{if(!nodes.has(q))nodes.set(q,{classList:{toggle(){}},dataset:{}});return nodes.get(q);};
 const ctx={document:{querySelector:el,querySelectorAll:()=>[]},URL,window:{TARIHIZ_CONFIG:{}},matchMedia:()=>({matches:true}),setInterval(){}};
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),ctx);
 const topics=require('../pilot-konular-taslak.json').konular.slice().sort((a,b)=>a.sort_order-b.sort_order);
 ctx.showTopics(topics);assert.match(el('#screen').innerHTML,/1\. Göbeklitepe/);assert.match(el('#screen').innerHTML,/5\. Rize/);
 const html=ctx.sourceHTML(topics[4].sources[0]);assert.match(html,/Minibüs Yerine Kamyon/);assert.match(html,/Pazartesi ve Cuma/);assert.match(html,/26 Ağustos 2024/);assert.match(html,/Çekim tarihi/);
});

test('Tarayıcı oturumu yenilenir, son yanıtta tamamlanma açılır, yeni katılımcı ayrılır',async()=>{
 const nodes=new Map(),saved=new Map();
 const el=q=>{if(!nodes.has(q))nodes.set(q,{dataset:{},value:'',scrollTop:0,classList:{toggle(){}},querySelectorAll(){return []},setAttribute(){},removeAttribute(){}});return nodes.get(q);};
 const action={dataset:{action:'final'}},topic={dataset:{topic:'T'}};
 const rows=[{id:'T',title:'Konu',stage:'final'}];let sessions=0,logouts=0;
 const ctx={document:{querySelector:el,querySelectorAll:q=>q==='[data-action]'?[action]:q==='[data-topic]'?[topic]:[]},URL,crypto:require('node:crypto').webcrypto,
 localStorage:{getItem:k=>saved.get(k),setItem:(k,v)=>saved.set(k,v),removeItem:k=>saved.delete(k)},clearTimeout,setInterval(){},matchMedia:()=>({matches:true}),
 window:{confirm:()=>true,TARIHIZ_CONFIG:{apiBase:'https://test.invalid',feedbackFormUrl:'https://forms.gle/test'}},
 fetch:async(url,opts)=>{
 if(url.endsWith('/anonymous-session')) {sessions++;return Response.json({token:'token',topics:rows});}
 if(url.endsWith('/logout')){logouts++;return Response.json({status:'ok'});}
 if(url.endsWith('/topics'))return Response.json(rows);
 if(JSON.parse(opts.body).action==='final')rows[0].stage='done';
 return Response.json({id:'W',topic_id:'T',revision:0,activity_snapshot:{id:'T',title:'Konu',question:'Soru?',sources:[{title:'Belge',text:'İçerik'}]},state:{stage:rows[0].stage,draft:'',messages:[],initial:{text:'ilk'},final:{text:'son'}}});
 }};
 const code=fs.readFileSync(path.join(__dirname,'../app.js'),'utf8');vm.runInNewContext(code,ctx);
 await el('#start').onclick();const credential=[...saved.values()][0];assert.equal(credential.length,64);
 assert.doesNotMatch(el('#screen').innerHTML,/Ankete Katıl|Katılım kodun/);
 await topic.onclick();el('#response').value='son';await action.onclick();
 assert.match(el('#screen').innerHTML,/Sorgulamayı Tamamladın/);assert.match(el('#screen').innerHTML,/Ankete Katıl/);
 // Fresh JS runtime, same localStorage: automatic resume to completion, without code input.
 const renewed={...ctx};vm.runInNewContext(code,renewed);await new Promise(setImmediate);
 assert.equal(sessions,2);assert.equal([...saved.values()][0],credential);
 assert.match(el('#screen').innerHTML,/Sorgulamayı Tamamladın/);
 await el('#newParticipant').onclick();assert.equal(logouts,1);assert.equal(saved.size,0);
 await el('#start').onclick();assert.notEqual([...saved.values()][0],credential);
});
