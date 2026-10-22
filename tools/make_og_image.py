#!/usr/bin/env python3
"""Draw the default 1200x630 share image (assets/og-image.png) from the site's own typography and colours.
Typographic only: no photographs or generated imagery. Needs Pillow and the Cormorant Garamond / EB Garamond
TTFs (Google Fonts, OFL); pass --fonts DIR if they are not in the default location."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
RUBRIC=(139,30,45);GOLD=(233,196,106);CREAM=(250,246,238);INK=(43,32,28)
def font(d,name,size,wght=None):
    f=ImageFont.truetype(str(next(Path(d).rglob(name))),size)
    if wght:
        try:f.set_variation_by_axes([wght])
        except Exception:pass
    return f
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fonts',default='/usr/share/fonts/truetype/sand-box/google');ap.add_argument('--out',default=str(ROOT/'assets/og-image.png'));a=ap.parse_args()
    W,H=1200,630;im=Image.new('RGB',(W,H),RUBRIC);d=ImageDraw.Draw(im)
    d.rectangle([28,28,W-29,H-29],outline=GOLD,width=3);d.rectangle([40,40,W-41,H-41],outline=(196,150,80),width=1)
    # cross mark from the site logo (same geometry as the favicon path, scaled)
    cx,cy,s=W//2,150,2.2
    d.ellipse([cx-66,cy-66,cx+66,cy+66],outline=GOLD,width=4)
    pts=[(29,12),(35,12),(35,26),(49,26),(49,32),(35,32),(35,52),(29,52),(29,32),(15,32),(15,26),(29,26)]
    d.polygon([(cx+(x-32)*s,cy+(y-32)*s) for x,y in pts],fill=GOLD)
    title=font(a.fonts,'CormorantGaramond-VariableFont_wght.ttf',92,700);sub=font(a.fonts,'EBGaramond-Italic-VariableFont_wght.ttf',38,400);small=font(a.fonts,'EBGaramond-VariableFont_wght.ttf',28,500)
    def centre(y,t,f,fill):
        w=d.textlength(t,font=f);d.text(((W-w)/2,y),t,font=f,fill=fill)
    centre(250,'Bibliotheca Catholica',title,CREAM)
    centre(365,'a library of libraries',sub,GOLD)
    d.line([(W/2-160,430),(W/2+160,430)],fill=GOLD,width=2)
    centre(455,'Catholic authors, Scripture, the Magisterium, and free reading editions',small,CREAM)
    centre(505,'bibliothecacatholica.com',small,GOLD)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);im.save(a.out,optimize=True);print(a.out,im.size)
if __name__=='__main__':main()
