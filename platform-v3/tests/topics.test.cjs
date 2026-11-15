const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {webcrypto,randomUUID,createHmac} = require('node:crypto');
const path = require('node:path');

// Runs the actual HTTP handler. Only the PostgREST and Gemini network boundaries are replaced.
function sandbox() {
  const env={ANONYMOUS_ENTRY_ENABLED:'true',CODE_PEPPER:'isolated-test',SUPABASE_URL:'https://db.invalid',SUPABASE_SERVICE_ROLE_KEY:'test',GEMINI_API_KEY:'test'};
  const hash=code=>createHmac('sha256',env.CODE_PEPPER).update(code).digest('hex');
  const topics=[],works=[],sessions=[],prompts=[];
  const participants=['student1','student2'].map(code=>({id:randomUUID(),active:true,code_hash:hash(code)}));
  const tables={tarihiz_topics:topics,tarihiz_topic_works:works,tarihiz_sessions:sessions,tarihiz_participants:participants};
  const add=title=>{
    const topic={id:randomUUID(),pilot:true,title,question:title+' hangi yorumu destekler?',demo:true,sources:[{id:randomUUID(),title,text:'Örnek belge'}]};
    topics.push(topic);return topic;
  };
  async function fakeFetch(address,opts) {
    const url=new URL(address);
    const body=opts.body && JSON.parse(opts.body);
    if(url.hostname==='generativelanguage.googleapis.com') {
      prompts.push(JSON.parse(body.contents[0].parts[0].text));
      return Response.json({candidates:[{finishReason:'STOP',content:{parts:[{text:JSON.stringify({feedback:'Yorumunu henüz belirli bir ayrıntıya bağlamadın.',question:'Hangi ayrıntıyı kanıt gösterirsin?',ready:true})}]}}]});
    }
    assert.equal(url.hostname,'db.invalid');
    if(url.pathname.endsWith('tarihiz_rate_allow')) return Response.json(true);
    const table=tables[url.pathname.split('/').pop()];
    const matches=table.filter(row=>[...url.searchParams].every(([key,v])=>{
      if(v.startsWith('eq.')) return String(row[key])===v.slice(3);
      if(v.startsWith('gt.')) return row[key]>v.slice(3);
      return true;
    }));
    if(table===topics && url.searchParams.get('order')==='sort_order.asc,title.asc,id.asc') matches.sort((a,b)=>(a.sort_order??1000)-(b.sort_order??1000)||a.title.localeCompare(b.title)||a.id.localeCompare(b.id));
    if(opts.method==='PATCH') matches.forEach(row=>Object.assign(row,body));
    if(opts.method==='DELETE') { for (const row of matches) table.splice(table.indexOf(row),1);return Response.json(matches); }
    if(opts.method==='POST') {
      if(table===participants && participants.some(p=>p.code_hash===body.code_hash)) return Response.json([]);
      if(table!==works || !works.some(w=>w.topic_id===body.topic_id && w.participant_id===body.participant_id))
        table.push({id:randomUUID(),revision:0,created_at:new Date().toISOString(),...body});
      return Response.json([]);
    }
    if(url.searchParams.get('select')?.includes('stage:')) return Response.json(matches.map(w=>({topic_id:w.topic_id,stage:w.state.stage})));
    return Response.json(matches);
  }
  let handler;
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../supabase/functions/tarihiz-api/index.ts'),'utf8'),{
    Deno:{env:{get:k=>env[k]},serve:f=>handler=f},crypto:webcrypto,TextEncoder,URL,Response,structuredClone,AbortSignal,fetch:fakeFetch
  });
  async function api(route,token,body,status=200) {
    const response=await handler(new Request('https://edge.invalid/tarihiz-api'+route,{
      method:body?'POST':'GET',headers:token?{Authorization:'Bearer '+token}:{},body:body && JSON.stringify(body)
    }));
    const result=await response.json(); assert.equal(response.status,status,JSON.stringify(result)); return result;
  }
  return {api,add,topics,works,prompts,participants,sessions,env};
}
test('Anonim öğrenci ve konu akışı',async t=>{
  const {api,add,works,prompts}=sandbox();
  const a=add('Pazar'),b=add('Esnaf');
  const login=async code=>api('/session',null,{code});
  let token,w,other;
  const open=id=>api('/works',token,{topic_id:id});
  const act=(action,text,status=200)=>api('/works/'+w.id,token,{action,text,revision:w.revision},status);
  await t.test('Aynı kod yeni oturum açar',async()=>{
    token=(await login('student1')).token;
    const again=await login('student1');assert.notEqual(token,again.token);
    assert.deepEqual(again.topics.map(x=>x.stage),[null,null]);
  });
  await t.test('Konu başlığından seçim ve mükerrer açılış',async()=>{
    const pair=await Promise.all([open(b.id),open(b.id)]);w=pair[0];
    assert.equal(w.id,pair[1].id);assert.equal(works.length,1);
  });
  await t.test('Doğru soru ve kaynak geçmişe dönük korunur',async()=>{
    assert.deepEqual(w.activity_snapshot,b);
    b.title='Yeni ad';assert.equal((await open(b.id)).activity_snapshot.title,'Esnaf');
  });
  await t.test('Taslak yeniden girişte yüklenir',async()=>{
    w=await act('examine');w=await act('draft','Henüz yazıyorum');
    assert.equal((await open(b.id)).state.draft,'Henüz yazıyorum');
  });
  await t.test('İlk yanıt yalnızca bir kez gönderilir',async()=>{
    w=await act('initial','İlk yorum');
    await act('initial','değiştir',422);assert.equal(w.state.initial.text,'İlk yorum');
  });
  await t.test('Yarım çalışma sonraki oturumda aynı aşamada açılır',async()=>{
    const session=await login('student1');token=session.token;
    assert.equal(session.topics.find(x=>x.id===b.id).stage,'chat');
    assert.deepEqual(await open(b.id),w);
  });
  await t.test('Diyalog ve kaynakla ilişkili Gemini isteği kaydedilir',async()=>{
    await act('finishChat',null,422);w=await act('ask');await act('finishChat',null,422);
    assert.deepEqual(prompts[0].activity,w.activity_snapshot);
    assert.equal(prompts[0].initial.text,'İlk yorum');
    assert.ok(w.state.messages[0].feedback);
    w=await act('reply','?');
    assert.deepEqual(w.state.messages.map(m=>m.role),['assistant','student']);
    assert.ok(w.state.messages.every(m=>Date.parse(m.at)));
  });
  await t.test('Kısa yanıt sonrası öğrenci sorgulamayı bitirebilir',async()=>{
    w=await act('finishChat');assert.equal(w.state.stage,'final');
  });
  await t.test('Son değerlendirme ilk yanıttan ayrı saklanır',async()=>{
    w=await act('final','Son yorum');assert.equal(w.state.initial.text,'İlk yorum');
    assert.equal(w.state.final.text,'Son yorum');assert.ok(w.state.completedAt);
  });
  await t.test('Tamamlanan çalışma yeniden başlatılamaz veya değiştirilemez',async()=>{
    assert.deepEqual(await open(b.id),w);await act('final','tekrar',422);
    assert.equal((await login('student1')).topics.find(x=>x.id===b.id).stage,'done');
  });
  await t.test('Sonradan eklenen görsel geçmiş yanıtları korur',async()=>{
    b.sources[0].image='pilot-gorseller/esnaf/kaynak.jpg';
    b.sources[0].image_ready=true;
    b.sources[0].image_credit_url='https://commons.wikimedia.org/wiki/File:Example.jpg';
    b.sources[0].metadata={Görsel:'Öğretmen tarafından eklenen görsel'};
    const savedState=structuredClone(w.state);
    const savedQuestion=w.activity_snapshot.question;
    w=await open(b.id);
    assert.equal(w.activity_snapshot.sources[0].image,b.sources[0].image);
    assert.equal(w.activity_snapshot.sources[0].image_ready,true);
    assert.equal(w.activity_snapshot.sources[0].metadata.Görsel,'Öğretmen tarafından eklenen görsel');
    assert.equal(w.activity_snapshot.question,savedQuestion);
    assert.deepEqual(w.state,savedState);
  });
  await t.test('Aynı öğrenci iki konuda ayrı kayıt alır',async()=>{
    other=await open(a.id);assert.equal(other.participant_id,w.participant_id);
    assert.notEqual(other.id,w.id);assert.equal(other.state.initial,null);
  });
  await t.test('Yeni konu katalogda görünür',async()=>{
    const extra=add('Yeni konu');assert.ok((await api('/topics',token)).some(x=>x.id===extra.id));
  });
  await t.test('Sahiplik ve eski revizyon denetlenir',async()=>{
    const second=(await login('student2')).token;
    await api('/works/'+other.id,second,{action:'examine',revision:0},404);
    await api('/works/'+other.id,token,{action:'examine',revision:99},409);
  });
});
test('Pilot kataloğu, SQL ve eski kayıtların korunması', async()=>{
  const {topics,api,add,works}=sandbox();
  const pilots=require('../pilot-konular-taslak.json').konular;
  const sql=fs.readFileSync(path.join(__dirname,'../supabase/pilot.sql'),'utf8');
  assert.deepEqual(JSON.parse(sql.split('$topics$')[1]),pilots);
  const legacy=add('Eski demo');legacy.pilot=false;
  topics.push(...pilots);
  const session=await api('/session',null,{code:'student1'});
  assert.deepEqual(session.topics.map(t=>t.id),[...pilots].sort((a,b)=>a.sort_order-b.sort_order).map(t=>t.id));
  for(const t of pilots){
    const w=await api('/works',session.token,{topic_id:t.id});
    assert.equal(w.activity_snapshot.question,t.question);
    assert.ok(t.sources.length>=1);
    assert.deepEqual(w.activity_snapshot.sources,t.sources);
    for(const source of t.sources) assert.ok(fs.existsSync(path.join(__dirname,"..",source.image)));
    assert.equal(t.sources[0].image_ready,true);
    assert.ok(fs.existsSync(path.join(__dirname,"..",t.sources[0].image)));
    assert.ok(!/^https?:/.test(t.sources[0].image));
  }
  works.push({id:randomUUID(),participant_id:works[0].participant_id,topic_id:legacy.id});
  await api('/works',session.token,{topic_id:legacy.id},404);
  assert.equal(works.length,pilots.length+1);
});

test('Kodsuz oturum aynı kimliğe döner; farklı tarayıcı ayrılır ve eski kayıtlar korunur',async()=>{
 const {api,add,works,participants,sessions,env}=sandbox();const t=add('Konu');
 const a=await api('/anonymous-session',null,{resumeKey:'a'.repeat(64)});
 const w=await api('/works',a.token,{topic_id:t.id});
 await api('/works/'+w.id,a.token,{action:'examine',revision:0});
 const b=await api('/anonymous-session',null,{resumeKey:'a'.repeat(64)});
 assert.notEqual(a.token,b.token);assert.equal(participants.length,3);
 const resumed=await api('/works',b.token,{topic_id:t.id});assert.equal(resumed.id,w.id);assert.equal(resumed.state.stage,'initial');
 const c=await api('/anonymous-session',null,{resumeKey:'b'.repeat(64)});
 const other=await api('/works',c.token,{topic_id:t.id});assert.notEqual(other.participant_id,w.participant_id);
 await api('/works/'+w.id,c.token,{action:'initial',revision:1,text:'x'},404);
 await api('/anonymous-session',null,{resumeKey:'short'},422);
 await api('/logout',b.token,{});await api('/topics',b.token,null,401);assert.equal(works.length,2);
 // Expired session can be renewed with the same private browser credential.
 sessions.find(s=>s.participant_id===w.participant_id).expires_at='2000-01-01T00:00:00Z';
 const renewed=await api('/anonymous-session',null,{resumeKey:'a'.repeat(64)});
 assert.equal((await api('/works',renewed.token,{topic_id:t.id})).id,w.id);
 participants.find(p=>p.id===w.participant_id).active=false;
 await api('/anonymous-session',null,{resumeKey:'a'.repeat(64)},403);
 env.ANONYMOUS_ENTRY_ENABLED='false';await api('/anonymous-session',null,{resumeKey:'c'.repeat(64)},503);
 assert.equal(participants.length,4);
});
