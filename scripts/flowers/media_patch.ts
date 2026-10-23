import { parseSync } from 'rolldown/utils';
export function patchMedia(code:string, replacements:Record<string,{fallback:string,responsive:unknown}>) {
 const parsed=parseSync('published.js',code);
 if(parsed.errors.length)throw Error('Published JS parse failed');
 const found=new Map<string,any[]>();
 function visit(node:any){
  if(!node||typeof node!=='object')return;
  if(node.type==='Property'&&Object.hasOwn(replacements,node.key?.value)){
   const key=node.key.value;found.set(key,[...(found.get(key)??[]),node.value]);
  }
  for(const value of Object.values(node))if(Array.isArray(value))value.forEach(visit);else if(value&&typeof value==='object')visit(value);
 }
 visit(parsed.program);
 const patches:{source:string,start:number,end:number,before:string,after:string}[]=[];
 for(const [source,replacement]of Object.entries(replacements)){
  const values=found.get(source)??[];
  if(values.length!==2||values.filter(n=>n.type==='Literal'&&typeof n.value==='string').length!==1||values.filter(n=>n.type==='ObjectExpression').length!==1)throw Error('Expected one fallback and one responsive property: '+source);
  for(const node of values)patches.push({source,start:node.start,end:node.end,before:code.slice(node.start,node.end),after:JSON.stringify(node.type==='Literal'?replacement.fallback:replacement.responsive)});
 }
 patches.sort((a,b)=>a.start-b.start);
 let output='',cursor=0,restored='';
 for(const p of patches){if(p.start<cursor)throw Error('Overlapping media values');const untouched=code.slice(cursor,p.start);output+=untouched+p.after;restored+=untouched+p.before;cursor=p.end;}
 output+=code.slice(cursor);restored+=code.slice(cursor);
 if(restored!==code)throw Error('UI preservation failed');
 return {code:output,patches,nonMediaBytesPreserved:true};
}
