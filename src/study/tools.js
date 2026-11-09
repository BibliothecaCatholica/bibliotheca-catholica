import {bcv_parser} from 'bible-passage-reference-parser/esm/bcv_parser.js';
import * as lang from 'bible-passage-reference-parser/esm/lang/en.js';
import {Cite} from '@citation-js/core';
import '@citation-js/plugin-csl';
import '@citation-js/plugin-bibtex';
import '@citation-js/plugin-ris';

const parser=new bcv_parser(lang);
parser.set_options({testaments:'ona',book_alone_strategy:'ignore',book_sequence_strategy:'ignore'});
export function scripture(text){return parser.parse(text).osis_and_indices();}
export function citations(work,edition){
 const record={id:work.id+'-'+edition.id,type:'book',title:work.title,author:[{literal:work.author}],URL:edition.source,language:edition.language||'English'};
 record.translator=(edition.contributors||[]).filter(c=>/translator/i.test(c.role)).map(c=>({literal:c.name}));
 return new Cite([record]);
}
window.BCResearch={scripture,citations};
