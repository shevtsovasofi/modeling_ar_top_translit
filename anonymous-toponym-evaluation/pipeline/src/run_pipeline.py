import argparse,csv,json,hashlib,platform,sys
from pathlib import Path
from render import Renderer,norm,bare,clusters,MARKS

def sha256_file(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def preserve_marks(raw,pred):
 # Exact original base checked first, then preserve supplied marks per letter.
 if bare(raw)!=bare(pred):return pred
 a,b=clusters(raw),clusters(pred)
 if len(a)!=len(b):return pred
 return ''.join(c+(m if m else pm) for (c,m),(_,pm) in zip(a,b))

class Diacritizer:
 def __init__(self,path):
  import os
  os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
  import torch
  from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
  self.torch=torch
  self.t=AutoTokenizer.from_pretrained(path,local_files_only=True)
  self.m=AutoModelForSeq2SeqLM.from_pretrained(path,local_files_only=True).to('cuda' if torch.cuda.is_available() else 'cpu').eval()
 def __call__(self,texts):
  if not texts:return []
  x=self.t(texts,padding=True,return_tensors='pt')
  if x['input_ids'].shape[1]>256:raise ValueError('Input exceeds trained range (256 tokens); split job or review long input')
  with self.torch.inference_mode():y=self.m.generate(**x.to(self.m.device),max_new_tokens=256,num_beams=1,do_sample=False)
  return self.t.batch_decode(y,skip_special_tokens=True)

def main():
 p=argparse.ArgumentParser(description='Arabic-only input to EN/RU map labels. Offline inference.')
 p.add_argument('--input',required=True);p.add_argument('--output',required=True)
 p.add_argument('--model',default='runs/fine-tashkeel-seed42/best')
 p.add_argument('--profile',choices=['orthographic','phonetic'],default='orthographic')
 p.add_argument('--diacritize-scope',choices=['full','proper'],default='full')
 p.add_argument('--batch-size',type=int,default=16)
 p.add_argument('--vocalized-column',help='Use existing Arabic vocalization instead of running model (QA mode)')
 p.add_argument('--confirmed-generic-column',help='Explicit human-confirmed generic term; optional, not a model input')
 p.add_argument('--overrides',help='JSON list of object/country scoped verified labels')
 a=p.parse_args()
 if a.batch_size<1:p.error('batch-size must be positive')
 out=Path(a.output)
 if out.exists():p.error('Output exists; use a new output path')
 with open(a.input,encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f)
  if 'name_ar_unvocalized' not in (reader.fieldnames or []):p.error('Required column: name_ar_unvocalized')
  if a.vocalized_column and a.vocalized_column not in reader.fieldnames:p.error('Vocalized column not found')
  if a.confirmed_generic_column and a.confirmed_generic_column not in reader.fieldnames:p.error('Confirmed generic column not found')
  rows=list(reader)
 overrides=json.loads(Path(a.overrides).read_text()) if a.overrides else []
 renderer=Renderer(profile=a.profile,overrides=overrides)
 diacritizer=None if a.vocalized_column else Diacritizer(a.model)
 results=[]
 for start in range(0,len(rows),a.batch_size):
  batch=rows[start:start+a.batch_size];texts=[];metadata=[]
  for row in batch:
   raw=row['name_ar_unvocalized'];confirmed=row.get(a.confirmed_generic_column) if a.confirmed_generic_column else None
   override=renderer.lookup_override(raw,row.get('geonameid') or row.get('id'),row.get('country'))
   _,n,_=renderer.match(raw,confirmed)
   text=' '.join(norm(raw).split()[n:]) if a.diacritize_scope=='proper' else norm(raw)
   metadata.append((raw,confirmed,n,text,override));texts.append(text)
  generated=[r[a.vocalized_column] for r in batch] if a.vocalized_column else ['']*len(batch)
  if not a.vocalized_column:
   pending=[i for i,meta in enumerate(metadata) if not meta[4] and bare(meta[0])]
   decoded=diacritizer([texts[i] for i in pending])
   for i,value in zip(pending,decoded):generated[i]=value
   for i,meta in enumerate(metadata):
    if meta[4]:generated[i]=meta[0]
  for row,meta,pred in zip(batch,metadata,generated):
   raw,confirmed,n,text,override=meta
   if a.diacritize_scope=='proper' and not a.vocalized_column and not override:
    pred=' '.join(norm(raw).split()[:n]+[pred])
   # Retain original supplied marks, never silently replace them.
   pred=preserve_marks(raw,pred)
   result=renderer.render(raw,pred,confirmed,row.get('geonameid') or row.get('id'),row.get('country'))
   result['id']=row.get('geonameid') or row.get('id')
   result['diacritize_scope']=a.diacritize_scope
   if not bare(raw):
    result.update(status='rejected',final_en=None,final_ru=None)
    result['warnings'].append('empty_input')
   results.append(result)
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf-8') as f:
  for r in results:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 table=Path(str(out)+'.csv')
 with table.open('w',encoding='utf-8-sig',newline='') as f:
  fields=['id','name_ar_raw','proper_ar','proper_diacritized','final_en','final_ru','status','warnings']
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for r in results:
   record={k:r.get(k,'') for k in fields};record['warnings']=';'.join(r['warnings']);writer.writerow(record)
 import collections
 manifest={'arguments':{k: ('<path omitted>' if k in {'input','output','model','overrides'} and v else v) for k,v in vars(a).items()},'input_sha256':sha256_file(a.input),'python':platform.python_version(),'count':len(results),'statuses':dict(collections.Counter(r['status'] for r in results)),'warning_counts':dict(collections.Counter(w for r in results for w in r['warnings'])),'code_and_config_sha256':{str(p.resolve().relative_to(Path(__file__).resolve().parents[1])):sha256_file(p) for directory in [Path(__file__).parent,Path(__file__).resolve().parents[1]/'config'] for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts}}
 if not a.vocalized_column:
  import torch,transformers
  manifest.update(torch=torch.__version__,transformers=transformers.__version__,model_sha256={str(p.relative_to(Path(a.model))):sha256_file(p) for p in Path(a.model).rglob('*') if p.is_file() and '.cache' not in p.parts})
 Path(str(out)+'.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 print(json.dumps({k:manifest[k] for k in ['count','statuses','warning_counts']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
