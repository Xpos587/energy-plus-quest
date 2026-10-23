import os, time, json
from pathlib import Path
from google import genai
from google.genai import types
root=Path(__file__).parent
client=genai.Client(api_key=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ['GOOGLE_AI_API_KEY'])
upload=None
receipt={'source':'kling-6s.mp4','cleanup':False}
try:
    available={m.name for m in client.models.list()}
    model=next(m for m in ['gemini-3-flash-preview','gemini-2.5-flash'] if 'models/'+m in available)
    receipt['model']=model
    upload=client.files.upload(file=str(root/'kling-6s.mp4'))
    for _ in range(60):
        upload=client.files.get(name=upload.name)
        if upload.state.name=='ACTIVE': break
        if upload.state.name=='FAILED': raise RuntimeError('Video processing failed')
        time.sleep(2)
    else: raise RuntimeError('Video processing timed out')
    prompt="Review this entire 6second map video in Russian with timestamped evidence. Track FOUR trucks separately: red blue green yellow. Detect splitting duplicates disappearance reverse movement or driving into buildings. Cab and semitrailer must remain rigid, articulated at hitch rather than rigid sprite spinning or rubber bending. This is only a6second segment, not a loop. Check frame-to-frame continuity, whether the top-right two vehicles stay separate and whether trailers remain straight. Camera and background must be fixed. Give per-truck observations and explicit uncertain intervals. Distinguish observations and interpretation. Do not blindly PASS; never invent observed positions. Return FAIL if any hard defect. This is actual video analysis, not a prompt-following description."
    response=client.models.generate_content(model=model,contents=[types.Content(parts=[types.Part(file_data=types.FileData(file_uri=upload.uri,mime_type='video/mp4'),video_metadata=types.VideoMetadata(fps=8)),types.Part(text=prompt)])],config=types.GenerateContentConfig(temperature=0.1))
    (root/'gemini-review.md').write_text(response.text)
    receipt['usage']=response.usage_metadata.model_dump(mode='json') if response.usage_metadata else None
    print(response.text)
finally:
    if upload:
        client.files.delete(name=upload.name)
        receipt['cleanup']=True
    (root/'gemini-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
    print('Remote upload deleted:',receipt['cleanup'])
