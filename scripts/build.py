"""Build Miracle Grove from vendored, hash-verified Fraunces inputs.

Font software and build sources: SIL Open Font License 1.1; see OFL.txt.
"""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib.tables import otTables
from fontTools import agl

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.200"
# Fixed OpenType epoch timestamp (2026-10-27 00:00:00 UTC) for reproducible output.
BUILD_TIMESTAMP = 3875904000
STYLES = [("Regular",400,450),("Medium",500,550),("SemiBold",600,650),("Bold",700,750)]

def verify_inputs():
    lock = json.loads((ROOT / "upstream/lock.json").read_text())
    for filename, record in lock["files"].items():
        actual = hashlib.sha256((ROOT / "upstream" / filename).read_bytes()).hexdigest()
        if actual != record["sha256"]:
            raise ValueError(f"Upstream checksum mismatch: {filename}")

def make_base(label, weight, sourceweight, italic):
    style = label + (" Italic" if italic else "")
    upstream = ROOT / "upstream" / ("Fraunces-Italic.ttf" if italic else "Fraunces.ttf")
    f=instantiateVariableFont(TTFont(upstream),{'wght':sourceweight,'opsz':36,'SOFT':100,'WONK':0},inplace=True)
    if not italic:
     # Preserve the original rising stem and upper serif, redraw a returning foot.
     g=f['glyf']['l']; pts=list(g.coordinates); assert len(pts)==40
     right,top=pts[0]; left=pts[23][0]
     p=TTGlyphPen(None); p.moveTo((right,top)); p.lineTo((right,320))
     p.qCurveTo((right,115),(right+120,115));p.qCurveTo((right+170,115),(right+210,145))
     p.qCurveTo((right+255,160),(right+265,115));p.qCurveTo((right+280,60),(right+220,25))
     p.qCurveTo((right+120,-40),(right+30,-40));p.qCurveTo((left,-40),(left,245))
     p.lineTo(pts[23])
     # Quadratic runs from the original stem up around the angled top.
     p.qCurveTo(*pts[24:27]);p.qCurveTo(*pts[27:31]);p.qCurveTo(*pts[31:34]);p.lineTo(pts[34])
     p.qCurveTo(*pts[35:38]);p.qCurveTo(*pts[38:],pts[0]);p.closePath()
     f['glyf']['l']=p.glyph();f['glyf']['l'].recalcBounds(f['glyf'])
     old=f['hmtx']['l'][0];new=round(right+330);delta=new-old
     f['hmtx']['l']=(new,f['glyf']['l'].xMin)
     for gn in f.getGlyphOrder():
      gg=f['glyf'][gn]
      if gg.isComposite() and any(c.glyphName=='l' for c in gg.components):
       aw,lsb=f['hmtx'][gn];f['hmtx'][gn]=(aw+delta,lsb)
    names=f['name']; family='Miracle Grove'
    legacyfamily=family if label in ('Regular','Bold') else family+' '+label
    legacystyle=('Bold' if label=='Bold' else 'Regular')
    if italic: legacystyle='Bold Italic' if label=='Bold' else 'Italic'
    full=family+' '+style;ps=full.replace(' ','')
    vals={1:legacyfamily,2:legacystyle,3:'1.000;AM;'+ps,4:full,5:'Version 1.000',6:ps,16:family,17:style,
     10:'Animal Miracles companion family derived from Fraunces. Fixed softness and optical size; refined upright letterforms and italic l and f. Not an exact reconstruction of the image-generated logo.'}
    for nid in [1,2,3,4,5,6,16,17,10,18,21,22,25]: names.removeNames(nameID=nid)
    for nid,value in vals.items():
     names.setName(value,nid,3,1,0x409);names.setName(value,nid,1,0,0)
    for tag in ('STAT','DSIG'):
     if tag in f: del f[tag]
    os=f['OS/2'];os.usWeightClass=weight;os.fsType=0
    os.fsSelection &= ~((1<<0)|(1<<5)|(1<<6)|(1<<9))
    if italic:os.fsSelection|=1
    if label=='Bold':os.fsSelection|=1<<5
    if not italic and label!='Bold':os.fsSelection|=1<<6
    f['head'].macStyle=(1 if label=='Bold' else 0)|(2 if italic else 0)
    f['head'].fontRevision=1.0

    return f

def append_substitution(f,tag,mapping):
 table=f['GSUB'].table
 sub=otTables.SingleSubst();sub.mapping=mapping
 lookup=otTables.Lookup();lookup.LookupType=1;lookup.LookupFlag=0;lookup.SubTable=[sub];lookup.SubTableCount=1
 ix=len(table.LookupList.Lookup);table.LookupList.Lookup.append(lookup);table.LookupList.LookupCount=len(table.LookupList.Lookup)
 record=otTables.FeatureRecord();record.FeatureTag=tag;record.Feature=otTables.Feature();record.Feature.FeatureParams=None;record.Feature.LookupListIndex=[ix];record.Feature.LookupCount=1
 oldrecords=list(table.FeatureList.FeatureRecord);oldrecords.append(record)
 newrecords=sorted(oldrecords,key=lambda r:r.FeatureTag)
 remap={i:newrecords.index(r) for i,r in enumerate(oldrecords)}
 for script in table.ScriptList.ScriptRecord:
  langs=([script.Script.DefaultLangSys] if script.Script.DefaultLangSys else [])+[r.LangSys for r in script.Script.LangSysRecord]
  for lang in langs:
   lang.FeatureIndex=sorted([remap[i] for i in lang.FeatureIndex]+[remap[len(oldrecords)-1]])
   lang.FeatureCount=len(lang.FeatureIndex)
   if lang.ReqFeatureIndex!=65535:lang.ReqFeatureIndex=remap[lang.ReqFeatureIndex]
 table.FeatureList.FeatureRecord=newrecords;table.FeatureList.FeatureCount=len(newrecords)

def refine_alphabet(f):
    """Logo-led upright refinements; retain spacing and existing curve topology."""
    for gn in ('M','h','m','n','r','Q'):
        g=f['glyf'][gn]
        assert not g.isComposite(), gn
        coords=list(g.coordinates)
        start=0
        for contour,end in enumerate(g.endPtsOfContours):
            for i in range(start,end+1):
                x,y=coords[i];dx=dy=0
                if gn=='M':
                    # Lift the rounded central valley, fading before the stems.
                    center=f['hmtx'][gn][0]/2
                    influence=max(0,1-abs(x-center)/350)
                    dy=110*influence*max(0,1-y/850)
                elif gn in ('h','m','n') and contour>0:
                    # Ease the leaning right stem into a more upright shoulder.
                    pts=coords[start:end+1]
                    right=max(px for px,py in pts)
                    influence=max(0,min(1,(x-(right-550))/300))
                    dx=32*influence*max(0,min(1,(y-250)/400))
                elif gn=='r' and contour==0:
                    # Open space below the terminal without changing its reach.
                    right=max(px for px,py in coords[start:end+1])
                    influence=max(0,min(1,(x-(right-380))/220))
                    dy=48*influence*max(0,min(1,(975-y)/450))
                elif gn=='Q' and contour==2:
                    # Let the tail turn upward, echoing the returning l foot.
                    dx=0;dy=55*max(0,min(1,(x-1100)/400))
                g.coordinates[i]=(round(x+dx),round(y+dy))
            start=end+1
    for gn in ('K','R','e'):
        rec=RecordingPen();f.getGlyphSet()[gn].draw(rec)
        p=TTGlyphPen(None);current=None;contour=-1
        for op,args in rec.value:
            if op=='moveTo':contour+=1
            target=args[-1] if args else None
            if op=='lineTo' and current is not None:
                x,y=current;tx,ty=target
                if gn in ('K','R') and contour==1 and abs(ty-y)>250:
                    # Parallel bowed edges give the leg a restrained sweep.
                    p.qCurveTo(((x+tx)/2-65,(y+ty)/2),target)
                elif gn=='e' and abs(ty-y)<2 and abs(tx-x)>250 and 350<y<650:
                    p.qCurveTo(((x+tx)/2,y+36),target)
                else:p.lineTo(target)
            else:getattr(p,op)(*args)
            if target is not None:current=target
        f['glyf'][gn]=p.glyph()

def refine_font(f):
    italic=bool(f['OS/2'].fsSelection&1);cmap=f.getBestCmap()
    def encode(cp,gn):
     for t in f['cmap'].tables:
      if t.isUnicode() and (cp<=65535 or t.format in (12,13)):t.cmap[cp]=gn
    if italic:
     # Replace the looped l entrance with an angled, softly rounded stem cap.
     rec=RecordingPen();f.getGlyphSet()['l'].draw(rec)
     assert rec.value[6][0]=='lineTo' and rec.value[13][0]=='lineTo'
     right=rec.value[5][1][-1];left=rec.value[13][1][0]
     slope=(right[0]-rec.value[6][1][0][0])/(right[1]-rec.value[6][1][0][1])
     top=1440;rx=right[0]+slope*(top-right[1]);lx=left[0]+slope*(top-left[1])
     p=TTGlyphPen(None);p.moveTo((rx,top-45));p.lineTo(right)
     tail=RecordingPen();tail.value=rec.value[6:14];tail.replay(p)
     p.lineTo((lx-12,top-110));p.qCurveTo((lx-18,top-65),(lx+20,top-53))
     p.lineTo((rx-60,top+8));p.qCurveTo((rx+13,top+29),(rx,top-45));p.closePath()
     f['glyf']['l']=p.glyph()
     slash=RecordingPen();f.getGlyphSet()['lslash'].draw(slash)
     split=next(i for i,(op,_) in enumerate(slash.value) if op=='closePath')+1
     offset=slash.value[split][1][0][0]-rec.value[0][1][0][0]
     p=TTGlyphPen(None);stroke=RecordingPen();stroke.value=slash.value[:split];stroke.replay(p)
     f.getGlyphSet()['l'].draw(TransformPen(p,(1,0,0,1,offset,0)))
     f['glyf']['lslash']=p.glyph()
     # Keep f's identifying hook, but reduce its bulb and waist swell.
     g=f['glyf']['f']
     for i,(x,y) in enumerate(list(g.coordinates)):
      if y<0:x-=round(max(0,x-60)*.24*min(1,-y/140))
      if y>1150:x-=round(max(0,x-600)*.16)
      if 880<y<1120 and 450<x<650:x-=round(26*(1-abs(y-1000)/120))
      g.coordinates[i]=(x,y)
    if not italic:
     refine_alphabet(f)
     # The approved wordmark has an arched, lightly tapered A bridge.
     # Edit the base before decomposing so accented A forms inherit it.
     rec=RecordingPen();f.getGlyphSet()['A'].draw(rec)
     assert [op for op,_ in rec.value[:5]] == ['moveTo','lineTo','lineTo','lineTo','closePath']
     tl,tr,br,bl=[args[0] for _,args in rec.value[:4]]
     assert tl[1]==tr[1] and bl[1]==br[1]
     thickness=tl[1]-bl[1];rise=42;trim=round(thickness*.08)
     p=TTGlyphPen(None);p.moveTo(tl)
     p.qCurveTo(((tl[0]+tr[0])/2,tl[1]+2*rise),tr)
     p.lineTo(br)
     p.qCurveTo(((bl[0]+br[0])/2,bl[1]+2*(rise+trim)),bl)
     p.closePath()
     tail=RecordingPen();tail.value=rec.value[5:];tail.replay(p)
     f['glyf']['A']=p.glyph()
     g=f['glyf']['lj'];old_l_width=g.components[1].x
     g.components[1].x+=f['hmtx']['l'][0]-old_l_width
     # Slashed l keeps the new foot and a generous, distinct crossing stroke.
     p=TTGlyphPen(f.getGlyphSet());p.addComponent('l',(1,0,0,1,0,0))
     p.moveTo((10,640));p.lineTo((620,1030));p.lineTo((620,1170));p.lineTo((10,780));p.closePath()
     f['glyf']['lslash']=p.glyph();f['hmtx']['lslash']=(f['hmtx']['l'][0],10)
    # Recover useful pre-existing glyphs that were never encoded upstream.
    added=[]
    for gn in f.getGlyphOrder():
     uni=agl.toUnicode(gn)
     if len(uni)==1 and ord(uni) not in cmap and not 0xE000<=ord(uni)<=0xF8FF:
      encode(ord(uni),gn);added.append(f'U+{ord(uni):04X}')
    encode(0x2010,'hyphen')
    for cp,gn,width in [(0x2007,'figureSpace',max(f['hmtx'][cmap[ord(c)]][0] for c in '0123456789')),(0x202f,'narrowNoBreakSpace',round(f['hmtx']['space'][0]*.6))]:
     pen=TTGlyphPen(None);f['glyf'][gn]=pen.glyph();f['hmtx'][gn]=(width,0);encode(cp,gn)
    # Equal-width figures for donor totals and numerical columns.
    width=max(f['hmtx'][cmap[ord(c)]][0] for c in '0123456789');subs={}
    for ch in '0123456789':
     base=cmap[ord(ch)];gn=base+'.tnum';p=TTGlyphPen(f.getGlyphSet());dx=round((width-f['hmtx'][base][0])/2)
     p.addComponent(base,(1,0,0,1,dx,0));f['glyf'][gn]=p.glyph();f['hmtx'][gn]=(width,f['hmtx'][base][1]+dx);subs[base]=gn
    append_substitution(f,'tnum',subs)
    append_substitution(f,'pnum',{v:k for k,v in subs.items()})
    # Use simple contours in delivery fonts: avoid transformed/nested components.
    gs=f.getGlyphSet();replacement={}
    for gn in f.getGlyphOrder():
     if f['glyf'][gn].isComposite():
      rec=DecomposingRecordingPen(gs);gs[gn].draw(rec);p=TTGlyphPen(None);rec.replay(p);replacement[gn]=p.glyph()
    for gn,g in replacement.items():f['glyf'][gn]=g
    for gn in f.getGlyphOrder():
     g=f['glyf'][gn];g.recalcBounds(f['glyf'])
     if g.numberOfContours:f['hmtx'][gn]=(f['hmtx'][gn][0],g.xMin)
    # Caret positions permit cursor placement within fi/fl/ff ligatures.
    temp=TTFont();temp.setGlyphOrder(f.getGlyphOrder());fw=f['hmtx']['f'][0]
    carets=f'table GDEF {{ LigatureCaretByPos f_f {fw}; LigatureCaretByPos fi {fw}; LigatureCaretByPos fl {fw}; LigatureCaretByPos f_f_i {fw} {fw*2}; LigatureCaretByPos f_f_l {fw} {fw*2}; }} GDEF;'
    addOpenTypeFeaturesFromString(temp,carets);f['GDEF']=temp['GDEF']
    for rec in f['GSUB'].table.FeatureList.FeatureRecord:
     if rec.FeatureTag=='ss01':
      prm=otTables.FeatureParamsStylisticSet();prm.Version=0;prm.UINameID=300;rec.Feature.FeatureParams=prm
    f['name'].setName('Expressive alternate forms',300,3,1,0x409)
    f['name'].names=[n for n in f['name'].names if n.platformID!=1]
    style=f['name'].getDebugName(17)
    if style=='Regular Italic':f['name'].setName('Italic',17,3,1,0x409)
    f['name'].setName('Version '+VERSION,5,3,1,0x409)
    f['name'].setName(VERSION+';AM;'+f['name'].getDebugName(6),3,3,1,0x409)
    f['head'].fontRevision=float(VERSION)
    weight=f['OS/2'].usWeightClass
    buildStatTable(f,[dict(tag='wght',name='Weight',ordering=0,values=[dict(value=weight,name={400:'Regular',500:'Medium',600:'SemiBold',700:'Bold'}[weight],flags=2 if weight==400 else 0)]),dict(tag='ital',name='Italic',ordering=1,values=[dict(value=int(italic),name='Italic' if italic else 'Roman',flags=0 if italic else 2,**({} if italic else {'linkedValue':1}))])])
    f['name'].names=[n for n in f['name'].names if n.platformID!=1]

    return f

def build(output):
    verify_inputs()
    output = Path(output)
    for directory in (output / "ttf", output / "web"):
        directory.mkdir(parents=True, exist_ok=True)
    manifest = {}
    css = []
    for label, weight, sourceweight in STYLES:
        for italic in (False, True):
            font = refine_font(make_base(label, weight, sourceweight, italic))
            font.recalcTimestamp = False
            font["head"].created = BUILD_TIMESTAMP
            font["head"].modified = BUILD_TIMESTAMP
            filename = "MiracleGrove-" + label + ("Italic" if italic else "")
            for directory, suffix, flavor in (("ttf", ".ttf", None),("web", ".woff2", "woff2")):
                font.flavor = flavor
                path = output / directory / (filename + suffix)
                font.save(path)
                manifest[str(path.relative_to(output)).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
            style = "italic" if italic else "normal"
            css.append(f'@font-face {{\n  font-family: "Miracle Grove";\n  src: url("{filename}.woff2?v={VERSION}") format("woff2");\n  font-weight: {weight};\n  font-style: {style};\n  font-display: swap;\n}}')
    (output / "web/miracle-grove.css").write_text("\n\n".join(css)+"\n", encoding="utf-8")
    (output / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(f"Built {len(manifest)} font files in {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "fonts")
    build(parser.parse_args().output)
