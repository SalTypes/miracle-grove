"""Run FontBakery and preserve its full output; OFL-1.1."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build/audit';out.mkdir(parents=True,exist_ok=True)
command=[sys.executable,'-m','fontbakery','check-universal',*[str(p.relative_to(ROOT)) for p in sorted((ROOT/'fonts/ttf').glob('*.ttf'))],'--json',str(out/'fontbakery.json'),'--no-progress','--loglevel','WARN']
with (out/'fontbakery.txt').open('w',encoding='utf-8') as stream:run=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
if not (out/'fontbakery.json').exists():raise SystemExit(run.returncode or 1)
result=json.loads((out/'fontbakery.json').read_text())['result'];print(json.dumps(result,indent=2))
raise SystemExit(1 if run.returncode or any(result.get(k,0) for k in ('ERROR','FAIL','FATAL','(not finished)')) else 0)
