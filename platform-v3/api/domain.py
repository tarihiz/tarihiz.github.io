"""Sunucu tarafından uygulanan sıralama ve değişmez ilk yanıt kuralları."""
from copy import deepcopy

TABLE = ('evidence', 'strengths', 'limits', 'judgment')
COMPARE = ('support', 'conflict', 'result')
KEYS = {0:'meta', 1:'documentNote', 2:'singleFirst', 3:'singleDraft', 4:'singleFinal', 7:'multiFirst', 8:'multiDraft', 9:'multiFinal', 10:'conclusion'}

def initial_state():
    return {'cursor':0,'unlocked':0,'answers':{'meta':'','metaAddendum':'','documentNote':'','singleFirst':dict.fromkeys(TABLE,''),'singleFinal':dict.fromkeys(TABLE,''),'multiFirst':dict.fromkeys(COMPARE,''),'multiFinal':dict.fromkeys(COMPARE,''),'conclusion':'','singleDraft':'','multiDraft':''},'chats':{'single':{'messages':[],'ready':False},'multi':{'messages':[],'ready':False}}}

def filled(value):
    if isinstance(value,str): return bool(value.strip())
    return isinstance(value,dict) and bool(value) and all(isinstance(x,str) and bool(x.strip()) for x in value.values())

def is_locked(step, unlocked):
    return (step==0 and unlocked>0) or (step==2 and unlocked>2) or (step==4 and unlocked>5) or (step==7 and unlocked>7) or (step in (9,10) and unlocked>10)

def save_values(state, step, values):
    if step!=state['cursor'] or step not in KEYS: raise ValueError('Bu aşamada kayıt yapılamaz.')
    key = 'metaAddendum' if step == 0 and state['unlocked'] > 0 else KEYS[step]
    if key != 'metaAddendum' and is_locked(step,state['unlocked']): raise ValueError('Kaydedilmiş değerlendirme değiştirilemez.')
    expected=TABLE if step in (2,4) else COMPARE if step in (7,9) else None
    if expected:
        if not isinstance(values,dict) or set(values)!=set(expected): raise ValueError('Değerlendirme alanları geçersiz.')
        texts=values.values()
    else:
        texts=[values]
    if any(not isinstance(t,str) or len(t)>12000 for t in texts): raise ValueError('Yanıt 12.000 karakteri aşamaz.')
    result=deepcopy(state);result['answers'][key]=values
    return result

def move(state,target):
    s=deepcopy(state);i=s['cursor']
    if target!='next':
        try: j=int(target)
        except (ValueError,TypeError): raise ValueError('Geçersiz aşama.')
        if not 0<=j<=s['unlocked']: raise ValueError('Tamamlanmamış aşamalar atlanamaz.')
        s['cursor']=j;return s
    if i==11: return s
    if i==s['unlocked']:
        if i in (0,2,4,7,9,10) and not filled(s['answers'][KEYS[i]]): raise ValueError('Bu aşamadaki bütün alanları doldur.')
        if i in (3,8) and not s['chats']['single' if i==3 else 'multi']['ready']: raise ValueError('Yapay zekâ sorgulaması henüz tamamlanmadı.')
        s['unlocked']=i+1
    s['cursor']=i+1
    return s
