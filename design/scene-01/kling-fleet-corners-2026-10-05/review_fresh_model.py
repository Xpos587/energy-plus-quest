import os,json,base64,urllib.request,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parent
rois={'0-1':(610,95,1035,290),'1-mid':(345,50,855,285),'mid-2':(345,75,610,680),'2-3':(595,210,945,635),'3-0':(745,130,1040,630)}
directions={'0-1':'UP→LEFT','1-mid':'LEFT→DOWN-LEFT first half-corner; opening hold allowed','mid-2':'DOWN-LEFT→DOWN remaining half-corner','2-3':'DOWN→RIGHT','3-0':'RIGHT→UP'}
def one(name):
 color,seg=name.split('-',1);canvas=Image.new('RGB',(1440,1120),'white');d=ImageDraw.Draw(canvas)
 for i in range(16):
  t=i/3;f=root/f'fresh-{name}-{i:02}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(min(t,5)),'-i',str(root/f'{name}.mp4'),'-frames:v','1',str(f)],check=True)
  im=Image.open(f).crop(rois[seg]);im.thumbnail((355,245));x=(i%4)*360;y=(i//4)*280;canvas.paste(im,(x,y+25));d.text((x+5,y+5),f'{t:.3f}s',fill='black')
 out=root/f'fresh-{name}-contact.jpg';canvas.save(out,quality=95)
 prompt=f'You are a fresh independent skeptical reviewer. Analyze chronological actual-video crops at labeled timestamps0–5seconds, NOT generation instructions. One {color} tractor attached to one cream tarp semitrailer should drive {directions[seg]}. Check cab-first steering with trailer articulating rather than rigid-sprite spinning; cab/rear swaps, duplication, vanishing, reversing, roof/sidewalk overlaps, trailer geometry. Explain concrete visible failures with timestamps, distinguish projection foreshortening from deformation. Driver requirement1adult+emptypassengerseat; mark UNCERTAIN when unreadable. Soft clean illustrated style, no false physics assertions. Give motion PASS/FAIL/CONDITIONAL and exact limitations. Opening hold may be trimmed; not automaticFAIL. Respond briefly in Russian. You have no prior review information.'
 payload={'model':'gpt-5.6-sol','reasoning_effort':'medium','messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(out.read_bytes()).decode()}}]}]}
 req=urllib.request.Request(os.environ['NINEROUTER_URL'].rstrip('/')+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+os.environ['NINEROUTER_KEY'],'Content-Type':'application/json'})
 try:
  response=json.load(urllib.request.urlopen(req,timeout=240));text=response['choices'][0]['message']['content'];(root/f'fresh-review-{name}.md').write_text(text);(root/f'fresh-review-{name}-receipt.json').write_text(json.dumps({'model':'gpt-5.6-sol','reasoning_effort':'medium','source':str(root/f'{name}.mp4'),'evidence':str(out),'coverage':'16 cropped actual frames from0 through5s; not entire continuous playback','usage':response.get('usage')},indent=2));print(name,'REVIEWED',flush=True)
 except Exception as e:(root/f'fresh-review-{name}-error.txt').write_text(str(e));print(name,type(e).__name__,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:list(p.map(one,[f'{c}-{s}' for c in ['red','yellow'] for s in directions]))
