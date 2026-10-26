#!/usr/bin/env python3
"""Derive the compact map geometry for the Rites & Liturgy section from Natural Earth (public domain).

Run by hand only when the boundaries are refreshed; the output, data/rites-src/geo.json, is committed so
tools/build_rites.py and CI stay offline and reproducible.

    python3 tools/rites_geo.py NE_DIR
where NE_DIR holds, from https://github.com/nvkelso/natural-earth-vector (geojson/):
    ne_110m_admin_0_countries.geojson   world map
    ne_50m_admin_0_countries.geojson    insets, and Guam (absent at 1:110m)
    ne_50m_admin_1_states_provinces.geojson   Kerala locator outline only

Join key: ISO_A2_EH (ISO_A2 is -99 for a few countries). Projection: plain equirectangular, which is honest
about being a schematic. Coordinates are rounded to 0.1 px after Douglas-Peucker simplification.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W=1000.0;K=W/360.0;NORTH,SOUTH=84.0,-57.0;H=round((NORTH-SOUTH)*K,1)
# Insets: (id, title, lon0, lon1, lat0, lat1, width in px). Shading in an inset is still by country.
INSETS=[('lebanon','Lebanon',34.9,36.9,32.9,34.8,150),('holy-land','The Holy Land',34.0,36.4,29.3,33.5,150),('kerala','Kerala (south India)',74.2,78.6,7.9,13.0,150)]
NAME_FIX={'US':'United States','RU':'Russia','CN':'China','CI':"Côte d'Ivoire",'GM':'The Gambia','CZ':'Czechia','KR':'South Korea','KP':'North Korea','LA':'Laos','VN':'Vietnam','SY':'Syria','IR':'Iran','BO':'Bolivia','TZ':'Tanzania','MD':'Moldova'}
def dp(pts,tol):
    if len(pts)<3:return pts
    keep=[False]*len(pts);keep[0]=keep[-1]=True;st=[(0,len(pts)-1)]
    while st:
        a,b=st.pop();ax,ay=pts[a];bx,by=pts[b];dx,dy=bx-ax,by-ay;L=(dx*dx+dy*dy)**.5;m,mi=-1,-1
        for i in range(a+1,b):
            px,py=pts[i];d=abs(dy*px-dx*py+bx*ay-by*ax)/L if L>1e-9 else ((px-ax)**2+(py-ay)**2)**.5  # closed ring: distance to the start
            if d>m:m,mi=d,i
        if m>tol:keep[mi]=True;st+=[(a,mi),(mi,b)]
    return [p for p,k in zip(pts,keep) if k]
def clip(r,box):
    """Sutherland-Hodgman clip of one ring to a lon/lat rectangle (insets only)."""
    l0,l1,b0,b1=box
    for inside,cut in ((lambda p:p[0]>=l0,lambda a,b:(l0,a[1]+(b[1]-a[1])*(l0-a[0])/(b[0]-a[0]))),(lambda p:p[0]<=l1,lambda a,b:(l1,a[1]+(b[1]-a[1])*(l1-a[0])/(b[0]-a[0]))),
                       (lambda p:p[1]>=b0,lambda a,b:(a[0]+(b[0]-a[0])*(b0-a[1])/(b[1]-a[1]),b0)),(lambda p:p[1]<=b1,lambda a,b:(a[0]+(b[0]-a[0])*(b1-a[1])/(b[1]-a[1]),b1))):
        out=[]
        for i in range(len(r)):
            cur,prev=r[i],r[i-1]
            if inside(cur):
                if not inside(prev):out.append(cut(prev,cur))
                out.append(cur)
            elif inside(prev):out.append(cut(prev,cur))
        r=out
        if not r:break
    return r+[r[0]] if r else r
def rings(geom):
    if geom['type']=='Polygon':return geom['coordinates']
    return [r for poly in geom['coordinates'] for r in poly]
def path(geom,proj,tol,minarea=0.0,box=None):
    out=[]
    for r in rings(geom):
        if box:
            r=clip([tuple(p[:2]) for p in r],box)
            if len(r)<4:continue
        pts=[proj(x,y) for x,y in r];pts=dp(pts,tol)
        if len(pts)<3:continue
        area=abs(sum(pts[i][0]*pts[i-1][1]-pts[i-1][0]*pts[i][1] for i in range(len(pts))))/2
        if area<minarea:continue
        q=[(round(x*10),round(y*10)) for x,y in pts];q=[p for i,p in enumerate(q) if i==0 or p!=q[i-1]]
        # absolute first point, then relative steps (shorter); units are 0.1 px
        f=lambda v:('%g'%(v/10))
        s='M'+f(q[0][0])+','+f(q[0][1])+'l'+' '.join(f(q[i][0]-q[i-1][0])+','+f(q[i][1]-q[i-1][1]) for i in range(1,len(q)))+'z'
        out.append(s)
    return ''.join(out)
def main(ne):
    ne=Path(ne);w110=json.loads((ne/'ne_110m_admin_0_countries.geojson').read_text());w50=json.loads((ne/'ne_50m_admin_0_countries.geojson').read_text())
    a1=json.loads((ne/'ne_50m_admin_1_states_provinces.geojson').read_text())
    proj=lambda x,y:((x+180)*K,(NORTH-y)*K)
    world={};names={}
    for f in w110['features']:
        p=f['properties'];c=p['ISO_A2_EH']
        if c in('-99','AQ') or not c:continue
        world[c]=world.get(c,'')+path(f['geometry'],proj,0.45,0.05);names[c]=NAME_FIX.get(c,p['NAME_LONG'])
    for f in w50['features']:  # small territories absent at 1:110m that the data needs
        p=f['properties'];c=p['ISO_A2_EH']
        if c=='GU':
            # Guam is about 0.3 px wide at this scale: draw a 3 px marker square so it can be shaded and seen
            x,y=proj(144.79,13.45);world[c]='M%g,%gh3v3h-3Z'%(round(x-1.5,1),round(y-1.5,1));names[c]=p['NAME_LONG']
    insets=[]
    for iid,title,l0,l1,b0,b1,px in INSETS:
        k=px/(l1-l0);pr=(lambda k,l0,b1:lambda x,y:((x-l0)*k,(b1-y)*k))(k,l0,b1);paths={}
        for f in w50['features']:
            p=f['properties'];c=p['ISO_A2_EH']
            if c=='-99':continue
            xs=[x for r in rings(f['geometry']) for x,y in r];ys=[y for r in rings(f['geometry']) for x,y in r]
            if max(xs)<l0 or min(xs)>l1 or max(ys)<b0 or min(ys)>b1:continue
            d=path(f['geometry'],pr,0.4,0,(l0-.05,l1+.05,b0-.05,b1+.05))
            if d:paths[c]=d
            names.setdefault(c,NAME_FIX.get(c,p['NAME_LONG']))
        extra={}
        if iid=='kerala':
            ker=[f for f in a1['features'] if f['properties'].get('name')=='Kerala' and f['properties'].get('iso_a2')=='IN']
            assert len(ker)==1,'Kerala outline not found in admin-1'
            extra['kerala']=path(ker[0]['geometry'],pr,0.4,0,(l0-.05,l1+.05,b0-.05,b1+.05))
        insets.append({'id':iid,'title':title,'w':px,'h':round((b1-b0)*k,1),'box':[l0,l1,b0,b1],'paths':paths,'outlines':extra})
    meta={'source':'Natural Earth, Admin 0 Countries 1:110m (world) and 1:50m (insets, Guam); Admin 1 States and Provinces 1:50m (Kerala outline only)',
          'version':'natural-earth-vector master (5.2.0-pre geojson), retrieved 2026-10-26','url':'https://github.com/nvkelso/natural-earth-vector',
          'terms':'https://www.naturalearthdata.com/about/terms-of-use/','rights':'public domain','join_key':'ISO_A2_EH','projection':'equirectangular, lat %g to %g'%(NORTH,SOUTH),'w':W,'h':H}
    out={'meta':meta,'names':dict(sorted(names.items())),'world':dict(sorted(world.items())),'insets':insets}
    p=ROOT/'data/rites-src/geo.json';p.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
    print(p,p.stat().st_size,'bytes;',len(world),'countries')
if __name__=='__main__':main(sys.argv[1])
