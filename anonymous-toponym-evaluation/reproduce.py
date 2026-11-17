"""Verify the frozen files and recompute, never adjust predictions to expected scores."""
from pathlib import Path
import hashlib,json,subprocess,sys,csv
root=Path(__file__).resolve().parent
for name,digest in json.loads((root/'SHA256SUMS.json').read_text()).items():
 p=root/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
  raise SystemExit('Integrity check failed: '+name)
result_dir=root/'results';result_dir.mkdir(exist_ok=True)
output=result_dir/'scores.json'
subprocess.run([sys.executable,str(root/'score_labels.py'),
 '--predictions',str(root/'data/predictions_original.jsonl'),
 '--references',str(root/'data/references_verified.csv'),
 '--id-column','geonameid','--en-column','reference_en','--ru-column','reference_ru',
 '--output',str(output)],check=True,capture_output=True,text=True)
scores=json.loads(output.read_text());expected=json.loads((root/'expected.json').read_text())
preds={r['id']:r for r in map(json.loads,(root/'data/predictions_original.jsonl').read_text().splitlines())}
with (root/'data/references_verified.csv').open(encoding='utf-8-sig',newline='') as f:refs=list(csv.DictReader(f))
from score_labels import canonical
for lang in ['en','ru']:
 actual=scores[lang]
 count=sum(canonical(preds[r['geonameid']]['final_'+lang])==canonical(r['reference_'+lang]) for r in refs)
 assert actual['n']==expected[lang]['n'] and count==expected[lang]['exact_count'], (lang,actual,count)
 assert abs(actual['character_f1']-expected[lang]['character_f1'])<1e-12,(lang,actual)
 actual['exact_count']=count
 print(f"{lang.upper()}: F1={actual['character_f1']:.4f}; exact={count}/{actual['n']}")
output.write_text(json.dumps(scores,ensure_ascii=False,indent=2))
print('PASS: checksums and recomputed metrics match. Detailed output: results/scores.json')
