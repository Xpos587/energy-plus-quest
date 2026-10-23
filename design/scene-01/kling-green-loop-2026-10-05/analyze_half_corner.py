import os,time,json
from pathlib import Path
from google import genai
from google.genai import types
root=Path(__file__).parent
client=genai.Client(api_key=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ['GOOGLE_AI_API_KEY'])
model='gemini-3-flash-preview'
for name in ['segment-2a','segment-2b']:
 source=root/'assembly'/f'{name}.mp4'
 if not source.exists(): continue
 upload=None
 receipt={'source':str(source),'cleanup':False,'model':model}
 try:
  upload=client.files.upload(file=str(source))
  for _ in range(60):
   upload=client.files.get(name=upload.name)
   if upload.state.name=='ACTIVE':break
   if upload.state.name=='FAILED':raise RuntimeError('Processing failed')
   time.sleep(2)
  else:raise RuntimeError('Processing timeout')
  prompt='Review actual entire five-second video in Russian with timestamped evidence. Exactly ONE green articulated truck should remain continuously visible, tractor steers first and rigid trailer follows via fifth-wheel; no rigid sprite spinning, reversing, duplication, disappearance, bending or roof/offroad overlap. Camera/background stationary. Detect whether it completes only one ninety-degree corner and straightens. Do NOT assume correctness from first/endframes. Distinguish uncertain observation from confirmed defect; return explicit PASS or FAIL with timestamps. Inspect wheels, cab and trailer continuity closely.'
  response=client.models.generate_content(model=model,contents=[types.Content(parts=[types.Part(file_data=types.FileData(file_uri=upload.uri,mime_type='video/mp4'),video_metadata=types.VideoMetadata(fps=8)),types.Part(text=prompt)])],config=types.GenerateContentConfig(temperature=.1))
  (root/f'gemini-{name}.md').write_text(response.text)
  receipt['usage']=response.usage_metadata.model_dump(mode='json') if response.usage_metadata else None
  print(name,response.text,flush=True)
 except Exception as e:
  receipt['error']=str(e);print(name,type(e).__name__,flush=True)
 finally:
  if upload:client.files.delete(name=upload.name);receipt['cleanup']=True
  (root/f'gemini-{name}-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
