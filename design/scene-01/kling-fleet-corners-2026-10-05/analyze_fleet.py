import os,time,json,concurrent.futures
from pathlib import Path
from google import genai
from google.genai import types
root=Path(__file__).parent
model='gemini-3-flash-preview'
directions={'0-1':'UP to LEFT, one ninety-degree corner','1-mid':'LEFT to DOWN-LEFT, only the first HALF of one corner; a stationary opening hold is allowed and can be trimmed','mid-2':'DOWN-LEFT to DOWN, remaining HALF of the same corner then straight down','2-3':'DOWN to RIGHT, one ninety-degree corner','3-0':'RIGHT to UP, one ninety-degree corner'}
def review(name):
 client=genai.Client(api_key=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ['GOOGLE_AI_API_KEY']);upload=None;receipt={'source':str(root/f'{name}.mp4'),'model':model,'cleanup':False}
 try:
  upload=client.files.upload(file=receipt['source'])
  for _ in range(60):
   upload=client.files.get(name=upload.name)
   if upload.state.name=='ACTIVE':break
   if upload.state.name=='FAILED':raise RuntimeError('Processing failed')
   time.sleep(2)
  else:raise RuntimeError('Processing timeout')
  color,segment=name.split('-',1)
  prompt=f'Independently inspect the ACTUAL ENTIRE five-second video at quarter-second precision. One {color} articulated road truck, tractor pulling one attached cream tarp semitrailer. Required movement: {directions[segment]}. Camera stationary. Inspect if cab steers first and rigid trailer follows at hitch rather than sprite spinning; cab must not become rear end, reverse, duplicate, disappear, teleport, bend, cross roofs/sidewalks. Exactly one driver with empty passenger seat; state UNCERTAIN if unreadable, never infer from prompt. Separate confirmed defect from uncertain foreshortening/compression. Give PASS/FAIL movement, exact timestamps and observable evidence. An opening hold is not a reverse. Minor change in projected trailer length during a turn is normal perspective, not automatically deformation. Answer concisely in Russian.'
  response=client.models.generate_content(model=model,contents=[types.Content(parts=[types.Part(file_data=types.FileData(file_uri=upload.uri,mime_type='video/mp4'),video_metadata=types.VideoMetadata(fps=8)),types.Part(text=prompt)])],config=types.GenerateContentConfig(temperature=.1))
  (root/f'gemini-{name}.md').write_text(response.text);receipt['usage']=response.usage_metadata.model_dump(mode='json') if response.usage_metadata else None;print(name,'REVIEWED',flush=True)
 except Exception as e:receipt['error']=str(e);print(name,type(e).__name__,flush=True)
 finally:
  if upload:
   try:client.files.delete(name=upload.name);receipt['cleanup']=True
   except Exception as e:receipt['cleanup_error']=str(e)
  (root/f'gemini-{name}-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(review,[f'{c}-{s}' for c in ['red','yellow'] for s in directions]))
