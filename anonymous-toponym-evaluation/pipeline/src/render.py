"""New project display profile, not a normative transliteration standard."""
import csv,json,unicodedata as U
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKS=set(chr(i) for i in range(0x64b,0x660))|{'\u0670'}
SUN=set('تثدذرزسشصضطظلن')
AR='ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي'.split()
EN='b t th j h kh d dh r z s sh s d t z \' gh f q k l m n h w y'.split()
RU='б т с дж х х д з р з с ш с д т з _ г ф к к л м н х в й'.split()
MAP={'en':dict(zip(AR,EN)),'ru':dict(zip(AR,RU))}
VOWELS={'َ':('a','а'),'ِ':('i','и'),'ُ':('u','у')}
def norm(s):return U.normalize('NFC',' '.join(s.split()))
def bare(s):return ''.join(c for c in norm(s) if c not in MARKS and c!='ـ')
def clusters(s):
 out=[]
 for c in norm(s):
  if c in MARKS:
   if out:out[-1][1]+=c
  elif c!='ـ':out.append([c,''])
 return out
def cap(s):return s[:1].upper()+s[1:]

def render_word(word,lang,profile='orthographic'):
 cs=clusters(word);flags=[];longs=[]
 if not cs:return '',flags,longs
 article=''
 if len(cs)>2 and cs[0][0] in 'اٱ' and cs[1][0]=='ل':
  body=cs[2:];solar=body[0][0] in SUN
  # Shadda inserted by article assimilation must not double the stem again.
  if solar:body[0][1]=body[0][1].replace('ّ','')
  if profile=='orthographic':article='Al ' if lang=='en' else 'Аль '
  elif solar:
   lead=MAP[lang][body[0][0]]
   article=('a' if lang=='en' else 'а')+lead+'-'
  else:article='al-' if lang=='en' else 'Аль-'
  cs=body
 result='';i=0
 while i<len(cs):
  c,m=cs[i];nxt=cs[i+1] if i+1<len(cs) else None
  if c in 'ًٌٍ' or any(x in m for x in 'ًٌٍ'):
   flags.append('case_ending_or_tanwin_requires_review')
  if c=='آ':result+=('a' if lang=='en' else 'а');longs.append({'index':i,'vowel':'a'});i+=1;continue
  if c=='ة':
   vowel='a' if lang=='en' else 'а'
   if not result.endswith(vowel):result+=vowel
   flags.append('ta_marbuta_pause_form_idafa_unverified');i+=1;continue
  if c in 'اأإؤئءٱى':
   if c in 'أإؤئء':cons="'" if lang=='en' and i>0 else ''
   elif c in 'اٱى':
    cons=('a' if lang=='en' else 'а') if c=='ى' else ''
    if not m:flags.append('incomplete_diacritization')
   else:cons=''
  elif c in MAP[lang]:cons=MAP[lang][c]
  elif c.isascii() and (c.isdigit() or c in '-.,()/'):
   result+=c;i+=1;continue
  else:
   flags.append('unsupported_character:'+c);result+=c;i+=1;continue
  if cons=='_':cons=''
  if c=='ع' and i==0:cons=''
  if 'ّ' in m:cons*=2
  result+=cons
  v=next((x for x in VOWELS if x in m),None)
  if len([x for x in 'َُِْ' if x in m])>1:flags.append('conflicting_marks')
  if v:
   vowel=VOWELS[v][0 if lang=='en' else 1]
   result+=vowel
   if v=='َ' and nxt and nxt[0] in 'وي' and 'ْ' in nxt[1]:
    result+=('w' if lang=='en' else 'у') if nxt[0]=='و' else ('y' if lang=='en' else 'й')
    i+=2;continue
   expected={'َ':'اى','ِ':'ي','ُ':'و'}[v]
   if nxt and nxt[0] in expected and not any(x in nxt[1] for x in 'ًٌٍَُِّ'):
    # Ya/waw with explicit sukun after fatha are diphthongs, not long vowels.
    longs.append({'index':i,'vowel':VOWELS[v][0]});i+=1
  elif i < len(cs)-1 and c in MAP[lang] and 'ْ' not in m and 'ّ' not in m:
   flags.append('incomplete_diacritization')
  elif i < len(cs)-1 and c in MAP[lang] and 'ّ' in m and 'ْ' not in m:
   flags.append('incomplete_diacritization')
  i+=1
 if profile=='phonetic' and article:
  return cap(article)+cap(result),flags,longs
 return article+cap(result),flags,longs

# Explicit English templates. All other dictionary entries need configuration.
SUFFIX={'شارع','طريق','طريق سريع','جسر','مطار','حديقة','جامعة','وادي','جزيرة'}
PREFIX={'جبل','بحيرة'}
AMBIGUOUS={'عين','رأس','راس','خور','وادي','قصر','حي','مركز'}
TITLES={'الملك':('King','Король'),'الشيخ':('Sheikh','Шейх'),'الأمير':('Prince','Принц')}
class Renderer:
 def __init__(self,dictionary=None,names=None,profile='orthographic',overrides=None):
  if profile not in ('orthographic','phonetic'):raise ValueError('Unknown article profile')
  self.profile=profile
  with open(dictionary or ROOT/'config/generic_terms_dictionary.csv',encoding='utf-8-sig',newline='') as f:self.terms=list(csv.DictReader(f))
  self.terms.sort(key=lambda r:(len(bare(r['ar_term']).split()),len(r['ar_term'])),reverse=True)
  self.names=json.loads(Path(names or ROOT/'config/names.json').read_text(encoding='utf-8'))
  self.overrides=overrides or []
 def match(self,text,confirmed_generic=None):
  tokens=bare(text).split()
  if not tokens or tokens[0]=='زهرة':return None,0,[]
  for r in self.terms:
   term=bare(r['ar_term']);tt=term.split();n=len(tt)
   if n>=len(tokens):continue # no empty proper-name component
   prefix=tokens[:n];article=False
   if prefix!=tt:
    prefix=prefix.copy()
    if prefix[0].startswith('ال'):prefix[0]=prefix[0][2:];article=True
    if prefix!=tt:continue
   confirmed=confirmed_generic is not None and bare(confirmed_generic)==term
   if article and not confirmed:return None,0,['ambiguous_generic']
   if term in AMBIGUOUS and not confirmed:return None,0,['ambiguous_generic']
   if term not in SUFFIX|PREFIX and not confirmed:return None,0,['generic_role_requires_confirmation']
   return r,n,[]
  return None,0,[]
 def own(self,text,lang):
  tokens=norm(text).split();output=[];flags=[];trace=[];i=0
  keys=sorted(self.names,key=lambda k:len(k.split()),reverse=True)
  while i<len(tokens):
   hit=next((k for k in keys if bare(' '.join(tokens[i:i+len(k.split())]))==k),None)
   if hit:
    entry=self.names[hit];output.append(entry[lang]);trace.append({'rule':'name_dictionary','key':hit,'origin':entry.get('origin')});i+=len(hit.split());continue
   k=bare(tokens[i])
   if k in TITLES and i==0 and len(tokens)>1:
    output.append(TITLES[k][0 if lang=='en' else 1]);trace.append({'rule':'initial_title','key':k});i+=1;continue
   value,w,longs=render_word(tokens[i],lang,self.profile)
   output.append(value);flags+=w
   trace.append({'rule':'transliteration','token':tokens[i],'long_vowels':longs})
   i+=1
  return ' '.join(output),flags,trace
 def lookup_override(self,raw,object_id=None,country=None):
  matches=[o for o in self.overrides if o.get('name_ar')==bare(raw) and
   (o.get('id') or o.get('country')) and
   (not o.get('id') or str(o['id'])==str(object_id)) and
   (not o.get('country') or o['country']==country)]
  if len(matches)>1:raise ValueError('Ambiguous label overrides')
  return matches[0] if matches else None
 def render(self,raw,vocalized,confirmed_generic=None,object_id=None,country=None):
  raw_normal=norm(raw);flags=[]
  # Overrides must be object/country scoped; no global homonym replacement.
  override=self.lookup_override(raw,object_id,country)
  base={'name_ar_raw':raw,'search_key':bare(raw),'profile':self.profile}
  if override:
   o=override
   if not o.get('source'):raise ValueError('Override requires source')
   return dict(base,final_en=o['en'],final_ru=o['ru'],warnings=[],rules=[{'rule':'verified_override','source':o['source']}],status='override')
  if bare(vocalized)!=bare(raw):
   return dict(base,vocalized=vocalized,final_en=None,final_ru=None,warnings=['model_changed_base'],rules=[],status='rejected')
  r,n,w=self.match(raw_normal,confirmed_generic);flags+=w
  original_tokens=raw_normal.split();vocal_tokens=norm(vocalized).split()
  if len(original_tokens)!=len(vocal_tokens):
   return dict(base,vocalized=vocalized,final_en=None,final_ru=None,warnings=['token_alignment_failed'],rules=[],status='rejected')
  proper=' '.join(vocal_tokens[n:]);rules=[];labels={}
  if r:rules.append({'rule':'generic_prefix','term':r['ar_term'],'origin':r['origin'],'token_end':n})
  if r and bare(r['ar_term']) not in SUFFIX|PREFIX:flags.append('missing_template')
  if r and len(proper.split()) > 1 and bare(proper.split()[0]) in TITLES:flags.append('russian_inflection_required')
  for lang in ['en','ru']:
   label,ws,tr=self.own(proper,lang);flags+=ws
   rules.extend(dict(t,language=lang) for t in tr)
   if r:
    if lang=='ru':label=cap(r['ru_term'])+' '+label
    elif bare(r['ar_term']) in PREFIX:
     label=('Mount' if bare(r['ar_term'])=='جبل' else 'Lake')+' '+label
    elif bare(r['ar_term']) in SUFFIX:label=label+' '+r['en_term']
    else:label=None
   labels[lang]=label
  return dict(base,generic=r,proper_ar=' '.join(original_tokens[n:]),proper_diacritized=proper,vocalized=vocalized,final_en=labels['en'],final_ru=labels['ru'],warnings=sorted(set(flags)),rules=rules,status='review' if flags else 'generated')
