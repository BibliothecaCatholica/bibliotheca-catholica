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
    # The Spanish Victory cross, with its trefoil terminals and Alpha/Omega,
    # adapted from the shared site mark and rendered in the existing palette.
    cx,cy=W//2,150
    d.ellipse([cx-66,cy-66,cx+66,cy+66],outline=GOLD,width=4)
    d.rounded_rectangle([cx-8,cy-47,cx+8,cy+44],radius=8,fill=GOLD)
    d.rounded_rectangle([cx-48,cy-13,cx+48,cy+3],radius=8,fill=GOLD)
    for x,y,r in ((0,-53,8),(-9,-45,6),(9,-45,6),(0,50,8),(-9,42,6),(9,42,6),(-53,-5,8),(-45,-14,6),(-45,4,6),(53,-5,8),(45,-14,6),(45,4,6)):
        d.ellipse([cx+x-r,cy+y-r,cx+x+r,cy+y+r],fill=GOLD)
    greek=font(a.fonts,'EBGaramond-VariableFont_wght.ttf',24,600)
    d.text((cx-34,cy+8),'Α',font=greek,fill=CREAM)
    d.text((cx+17,cy+8),'Ω',font=greek,fill=CREAM)
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
