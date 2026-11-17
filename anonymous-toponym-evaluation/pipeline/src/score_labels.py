"""Explicit character metric for the new implementation; not historical F1 reproduction."""
import argparse,csv,json,unicodedata
from pathlib import Path

def canonical(s):return unicodedata.normalize('NFC',' '.join((s or '').split()))
def matches(pred,gold):
 # Levenshtein alignment, ties prefer more matching characters.
 prev=[(j,0) for j in range(len(gold)+1)]
 for i,x in enumerate(pred,1):
  cur=[(i,0)]
  for j,y in enumerate(gold,1):
   candidates=[(prev[j][0]+1,prev[j][1]),(cur[j-1][0]+1,cur[j-1][1]),(prev[j-1][0]+(x!=y),prev[j-1][1]+(x==y))]
   cur.append(min(candidates,key=lambda t:(t[0],-t[1])))
  prev=cur
 return prev[-1][1]
def score(pairs):
 match=pn=gn=exact=0
 for p,g in pairs:
  p,g=canonical(p),canonical(g)
  match+=matches(p,g);pn+=len(p);gn+=len(g);exact+=p==g
 precision=match/pn if pn else 0.;recall=match/gn if gn else 0.
 return {'n':len(pairs),'exact_match':exact/len(pairs) if pairs else None,'character_precision':precision,'character_recall':recall,'character_f1':2*match/(pn+gn) if pn+gn else None,'matching_characters':match,'predicted_characters':pn,'reference_characters':gn}
def main():
 p=argparse.ArgumentParser();p.add_argument('--predictions',required=True);p.add_argument('--references',required=True);p.add_argument('--id-column',default='geonameid');p.add_argument('--en-column',required=True);p.add_argument('--ru-column',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 predictions=[json.loads(x) for x in Path(a.predictions).read_text().splitlines() if x.strip()]
 if any(not r.get('id') for r in predictions):raise ValueError('Every prediction needs an object id')
 ids=[str(r['id']) for r in predictions]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate prediction ids')
 byid=dict(zip(ids,predictions))
 with open(a.references,encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f)
  for c in [a.id_column,a.en_column,a.ru_column]:
   if c not in reader.fieldnames:raise ValueError('Missing reference column: '+c)
  refs=list(reader)
 refids=[str(r[a.id_column]) for r in refs]
 if len(refids)!=len(set(refids)) or any(not x for x in refids):raise ValueError('Missing/duplicate reference ids')
 missing=set(refids)-set(byid)
 if missing:raise ValueError(f'Missing predictions for {len(missing)} reference ids')
 result={'metric':'micro character F1 from Levenshtein alignment; NFC + whitespace normalization; case/punctuation preserved','extra_prediction_ids':len(set(ids)-set(refids))}
 for lang,col in [('en',a.en_column),('ru',a.ru_column)]:
  usable=[r for r in refs if canonical(r[col])]
  result[lang]=score([(byid[str(r[a.id_column])].get('final_'+lang) or '',r[col]) for r in usable])
  result[lang]['missing_reference_labels']=len(refs)-len(usable)
 Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
