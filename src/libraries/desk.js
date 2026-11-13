import Fuse from 'fuse.js';
import {sourceUrl, rankResources} from './logic.mjs';
const sourceDefinitions=[
 {id:'openlibrary',name:'Open Library',note:'Find works and editions. A catalog match does not guarantee a freely readable book.'},
 {id:'archive',name:'Internet Archive',note:'Find scanned editions. Some items require borrowing or have access restrictions.'},
 {id:'gutenberg',name:'Project Gutenberg',note:'Find downloadable transcriptions. Check the translator and edition, and local rights.'},
 {id:'worldcat',name:'WorldCat',note:'Find editions and library holdings. A record does not provide a free digital copy.'}
];
function mount(){
 const root=document.querySelector('.library-desk');if(!root||root.dataset.ready)return;
 root.dataset.ready='true';
 const form=root.querySelector('form'),select=root.querySelector('select'),input=root.querySelector('input'),note=root.querySelector('[role=status]');
 select.replaceChildren(...sourceDefinitions.map(s=>new Option(s.name,s.id)));select.disabled=false;
 const describe=()=>{note.textContent=sourceDefinitions.find(s=>s.id===select.value).note+' Your query is sent only when you submit.'};select.onchange=describe;describe();
 // Keep native form navigation so keyboard submit, popup preferences, and fallback work.
 form.onsubmit=event=>{const query=input.value.trim();if(!query){event.preventDefault();input.setCustomValidity('Enter a title, author, or subject.');input.reportValidity();return}input.setCustomValidity('');const url=new URL(sourceUrl(select.value,query));form.action=url.origin+url.pathname;input.name=[...url.searchParams.keys()][0];input.value=query};
 input.oninput=()=>input.setCustomValidity('');
}
window.BCLibraryDesk={mount,rank:(resources,q)=>rankResources(Fuse,resources,q)};
