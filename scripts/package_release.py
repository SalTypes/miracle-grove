"""Package checked fonts with their license and usage notes; OFL-1.1."""
import hashlib,zipfile
from pathlib import Path
from test_fonts import check_fonts
ROOT=Path(__file__).resolve().parents[1];check_fonts(ROOT/'fonts');out=ROOT/'dist';out.mkdir(exist_ok=True);archive=out/'Miracle-Grove-1.200.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 files=[(p,p.relative_to(ROOT/'fonts')) for p in (ROOT/'fonts').rglob('*') if p.is_file()]
 files += [(ROOT/n,Path(n)) for n in ('OFL.txt','AUTHORS.txt','README.md','CHANGELOG.md')]
 files += [(p,p.relative_to(ROOT)) for p in (ROOT/'documentation').glob('*') if p.is_file()]
 files += [(p,p.relative_to(ROOT)) for p in (ROOT/'qa').glob('*') if p.is_file()]
 for path,name in sorted(files,key=lambda pair:str(pair[1])):
  info=zipfile.ZipInfo('Miracle-Grove/'+name.as_posix(),(2026,10,27,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,path.read_bytes())
(out/(archive.name+'.sha256')).write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n');print(archive)
