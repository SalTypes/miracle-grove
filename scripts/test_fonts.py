"""Regression checks for the generated family; OFL-1.1."""
import argparse, hashlib, json, unicodedata
from pathlib import Path
from fontTools.ttLib import TTFont
import uharfbuzz as hb
ROOT=Path(__file__).resolve().parents[1]
SAMPLES=['Animal Miracles','ÁÉÍÓÚÜÑ áéíóúüñ ¿Cómo estás? ¡Sí!','fi fl ffi ffl fluffy offline','lj ĺ ľ ļ ŀ ḷ ḻ ł','AVATAR WA To Ty Yo ll la le li lo lu','€ £ $ ₹ 1,234.56 1.234,56 1\u202f234,56','Français Português Deutsch Türkçe Polski Čeština','“Care”—‘life’… (all) [animals]']
def check_fonts(directory,compare=None):
 directory=Path(directory);paths=sorted((directory/'ttf').glob('*.ttf'))
 assert len(paths)==8 and len(list((directory/'web').glob('*.woff2')))==8
 report=[];cmaps=[];metrics=[];names=set()
 for path in paths:
  f=TTFont(path,checkChecksums=2);cmap=f.getBestCmap()
  assert len(cmap)==639 and len(f.getGlyphOrder())==710
  assert all(t in f for t in ('GPOS','GSUB','GDEF','STAT')) and 'fvar' not in f
  assert f['OS/2'].fsType==0 and f['name'].getDebugName(5)=='Version 1.200'
  ps=f['name'].getDebugName(6);assert ps not in names;names.add(ps)
  cmaps.append(set(cmap));metrics.append(tuple(getattr(f['OS/2'],k) for k in ('sTypoAscender','sTypoDescender','sTypoLineGap','usWinAscent','usWinDescent')))
  for gn in f.getGlyphOrder():
   g=f['glyf'][gn];assert not g.isComposite(),gn
   if g.numberOfContours:
    assert f['hmtx'][gn][1]==g.xMin,gn
    assert g.yMax<=f['OS/2'].usWinAscent and -g.yMin<=f['OS/2'].usWinDescent,gn
  font=hb.Font(hb.Face(path.read_bytes()))
  def shape(text,features=None):
   b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(font,b,features or {})
   return [(i.codepoint,p.x_advance,p.x_offset,p.y_offset) for i,p in zip(b.glyph_infos,b.glyph_positions)]
  for s in SAMPLES:assert all(g[0] for g in shape(s)),(path.name,s)
  for s in ['áéíóúüñ','ÁÉÍÓÚÜÑ','ĺḷḻ','ČšŽç']:assert shape(s)==shape(unicodedata.normalize('NFD',s))
  assert len({shape(c,{'tnum':1})[0][1] for c in '0123456789'})==1
  assert len({shape(c,{'pnum':1})[0][1] for c in '0123456789'})>1
  assert len(shape('ffi'))<len(shape('ffi',{'liga':0}))
  assert sum(x[1] for x in shape('AV',{'kern':1}))!=sum(x[1] for x in shape('AV',{'kern':0}))
  web=TTFont(directory/'web'/(path.stem+'.woff2'));assert web.getBestCmap()==cmap
  for tag in ('glyf','hmtx','GPOS','GSUB','GDEF','STAT'):assert web[tag].compile(web)==f[tag].compile(f),(path.name,tag)
  report.append({'file':path.name,'characters':639,'glyphs':710,'shaping_samples':8,'normalization_cases':4,'status':'pass'})
 assert all(c==cmaps[0] for c in cmaps) and all(m==metrics[0] for m in metrics)
 for filename,expected in json.loads((directory/'SHA256SUMS.json').read_text()).items():
  assert hashlib.sha256((directory/filename).read_bytes()).hexdigest()==expected,filename
  if compare:assert (directory/filename).read_bytes()==(Path(compare)/filename).read_bytes(),filename
 print(json.dumps({'styles':report,'reproducible_comparison':bool(compare)},indent=2))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fonts',type=Path,default=ROOT/'fonts');p.add_argument('--compare',type=Path);a=p.parse_args();check_fonts(a.fonts,a.compare)
