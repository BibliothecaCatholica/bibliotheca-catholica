export function sourceUrl(id,query){
 const q=encodeURIComponent(query.trim().slice(0,200));
 const bases={openlibrary:'https://openlibrary.org/search?q=',archive:'https://archive.org/search?query=',gutenberg:'https://www.gutenberg.org/ebooks/search/?query=',worldcat:'https://search.worldcat.org/search?q='};
 if(!Object.hasOwn(bases,id))throw new Error('Unknown collection');
 return bases[id]+q;
}
export function rankResources(Fuse,resources,query){
 const terms=query.trim().split(/\s+/).filter(Boolean);if(!terms.length)return resources;
 // A multiword query must match every token, including across separate fields.
 const fuse=new Fuse(resources,{keys:[{name:'name',weight:3},'desc','tags','category'],threshold:.32,ignoreLocation:true});
 const ranks=terms.map(term=>new Map(fuse.search(term).map((r,i)=>[r.item,i])));
 return resources.filter(r=>ranks.every(m=>m.has(r))).sort((a,b)=>ranks.reduce((s,m)=>s+m.get(a)-m.get(b),0));
}
