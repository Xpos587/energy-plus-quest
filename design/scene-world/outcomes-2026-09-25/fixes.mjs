import {writeFile} from 'node:fs/promises';
const dir='design/scene-world/outcomes-2026-09-25';
const jobs=[['crane-petr','Edit this exact picture, preserve both workers, their expressions, their clothing, dock, background, camera and polished 2D drawing. Fix ONLY departing barge cargo: it must already carry LARGE BUNDLES OF STEEL PIPES tied down along deck, PLUS the modest gift carton. The barge cannot have an otherwise empty deck. Make barge longer if needed while preserving realistic proportions. Keep the separate delayed pipes on quay as well. No added labels.'],['lastmile-rover','Edit this exact illustration. Critical correction: this amphibious vehicle must be FLOATING IN OPEN WATER, not driving on ice or solid ground. Preserve body shape, blue color, four huge balloon tires, gift parcel visible in rear window, landscape and current refined 2D style. Replace continuous ice platform under rover with open blue river water. Water line reaches lower HALF of all tires, hull is buoyant, wheels partly submerged. Small separated thin fragments of broken first ice only around vehicle, gentle visible wake behind it. No white solid ice surface beneath vehicle. Vehicle upright safely floating, not sinking.']];
await Promise.all(jobs.map(async([id,prompt])=>{
 await writeFile(`${dir}/${id}-fix.txt`,prompt);
 const p=Bun.spawn(['higgsfield','generate','create','nano_banana_2','--image',`public/scene-art/outcomes/${id}.webp`,'--aspect_ratio','3:2','--resolution','2k','--wait','--json'],{stdin:new Blob([prompt]),stdout:'pipe',stderr:'pipe'});
 const [out,err,code]=await Promise.all([new Response(p.stdout).text(),new Response(p.stderr).text(),p.exited]);await writeFile(`${dir}/${id}-fix.json`,out);await writeFile(`${dir}/${id}-fix.log`,err);
 if(code){console.log(id,'FAILED');return;}const url=JSON.parse(out)[0].result_url;
 const d=Bun.spawn(['curl','-fsSL','--retry','3','--retry-all-errors',url,'-o',`${dir}/${id}-fix.png`]);await d.exited;
 const c=Bun.spawn(['magick',`${dir}/${id}-fix.png`,'-resize','1200x800>','-quality','88',`${dir}/${id}-fix.webp`]);await c.exited;console.log(id,'FIX READY');
}));
