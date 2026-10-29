"""Reproducible spacing study; run from the repository root."""
import argparse,json,unicodedata,hashlib
from importlib.metadata import version
from pathlib import Path
from functools import lru_cache
import freetype,uharfbuzz as hb
from PIL import Image,ImageDraw,ImageFont,ImageChops
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
SIZES=[16,24,36,48,72,112]
MODES={'default':{},'no-kerning':{'kern':0},'no-ligatures':{'liga':0},'alternates':{'ss01':1}}
def run(baseline):
 out=ROOT/'build/spacing-study';out.mkdir(parents=True,exist_ok=True)
 corpus=json.loads((ROOT/'qa/spacing-corpus.json').read_text(encoding='utf-8'));words=list(dict.fromkeys(w for group in corpus.values() for w in group))
 report={'engine_versions':{'freetype':'.'.join(map(str,freetype.version())),'uharfbuzz':version('uharfbuzz'),'pillow':version('pillow')},'opacity_threshold':160,'font_hashes':{},'baseline_hashes':{},'sizes_px':SIZES,'unique_entries':len(words),'shaping_runs':0,'raster_runs':0,'new_contacts':[],'styles':[]}
 ui=ImageFont.load_default(size=22)
 for path in sorted((ROOT/'fonts/ttf').glob('*.ttf')):
  data=path.read_bytes();report['font_hashes'][path.name]=hashlib.sha256(data).hexdigest();report['baseline_hashes'][path.name]=hashlib.sha256((baseline/path.name).read_bytes()).hexdigest();font=hb.Font(hb.Face(data));face=freetype.Face(str(path));oldfont=hb.Font(hb.Face((baseline/path.name).read_bytes()));oldface=freetype.Face(str(baseline/path.name))
  def shape(text,h,font=font):
   b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(font,b,h)
   assert all(i.codepoint for i in b.glyph_infos),(path.name,text)
   return [(i.codepoint,p.x_advance,p.x_offset,p.y_offset) for i,p in zip(b.glyph_infos,b.glyph_positions)]
  @lru_cache(None)
  def bitmap(gid,size,old=False):
   fac=oldface if old else face;fac.set_pixel_sizes(0,size);fac.load_glyph(gid,freetype.FT_LOAD_RENDER|freetype.FT_LOAD_NO_HINTING);slot=fac.glyph;b=slot.bitmap
   return (Image.frombytes('L',(b.width,b.rows),bytes(b.buffer)) if b.width*b.rows else None,slot.bitmap_left,slot.bitmap_top)
  def contacts(shaped,size,old=False):
   x=0;previous=None;total=0
   for gid,adv,dx,dy in shaped:
    mask,left,top=bitmap(gid,size,old);pos=(round((x+dx)*size/2000)+left,round(-dy*size/2000)-top)
    if mask is not None:
     if previous:
      pm,pp=previous;box=(max(pos[0],pp[0]),max(pos[1],pp[1]),min(pos[0]+mask.width,pp[0]+pm.width),min(pos[1]+mask.height,pp[1]+pm.height))
      if box[2]>box[0] and box[3]>box[1]:
       aa=mask.crop((box[0]-pos[0],box[1]-pos[1],box[2]-pos[0],box[3]-pos[1])).point(lambda p:255 if p>=160 else 0)
       bb=pm.crop((box[0]-pp[0],box[1]-pp[1],box[2]-pp[0],box[3]-pp[1])).point(lambda p:255 if p>=160 else 0)
       total+=ImageChops.multiply(aa,bb).histogram()[255]
     previous=(mask,pos)
    else:previous=None
    x+=adv
   return total
  for word in words:
   for mode,features in MODES.items():
    shaped=shape(word,features);report['shaping_runs']+=1
    assert shaped==shape(unicodedata.normalize('NFD',word),features),(path.name,word,mode,'NFD')
   current=shape(word,{});older=shape(word,{},oldfont)
   for size in SIZES:
    new=contacts(current,size);old=contacts(older,size,True);report['raster_runs']+=1
    if new>old:report['new_contacts'].append({'style':path.stem,'word':word,'size':size,'before':old,'after':new})
  sheet=Image.new('RGB',(1800,1150),'#fffdf6');d=ImageDraw.Draw(sheet);d.text((35,20),path.stem+' / default spacing / 1.300',font=ui,fill='#355e59')
  y=65
  for size in SIZES:
   d.text((35,y),str(size)+' px',font=ui,fill='#355e59');baseline_y=y+35+size*.8;x=170
   for word_index,word in enumerate(corpus['requested']):
    if size==112 and word_index==2:x=170;baseline_y+=size+25
    shaped=shape(word,{});xx=x
    for gid,adv,dx,dy in shaped:
     mask,left,top=bitmap(gid,size)
     if mask is not None:sheet.paste('#091e4b',(round(xx+dx*size/2000)+left,round(baseline_y-dy*size/2000)-top),mask)
     xx+=adv*size/2000
    x=xx+size*.6+25
   y+=size+70
  sheet.save(out/(path.stem+'.png'))
  # Corpus pages use fixed 36px text, with no logo-specific positioning.
  chunks=[words[i:i+60] for i in range(0,len(words),60)]
  for page,chunk in enumerate(chunks,1):
   im=Image.new('RGB',(1800,1600),'#fffdf6');draw=ImageDraw.Draw(im);draw.text((30,20),path.stem+' / corpus / 36px / page '+str(page),font=ui,fill='#355e59')
   for row,word in enumerate(chunk):
    x=35+(row//30)*880;y=90+(row%30)*49
    for gid,adv,dx,dy in shape(word,{}):
     mask,left,top=bitmap(gid,36)
     if mask is not None:im.paste('#091e4b',(round(x+dx*36/2000)+left,round(y-dy*36/2000)-top),mask)
     x+=adv*36/2000
   im.save(out/(path.stem+'-corpus-'+str(page)+'.png'))
  report['styles'].append(path.stem)
 (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in ('font_hashes','baseline_hashes')},ensure_ascii=False,indent=2))
 if report['new_contacts']:raise SystemExit('New raster contacts need review')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args();run(a.baseline)
