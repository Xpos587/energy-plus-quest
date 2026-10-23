import os,time,json
from pathlib import Path
from google import genai
from google.genai import types
P=Path(__file__).resolve().parent
video=P/'whole-map-v07.mp4'
assert video.exists()
key=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
assert key,'Private Gemini configuration missing'
client=genai.Client(api_key=key)
model='gemini-2.5-flash';client.models.get(model=model)
uploaded=None;receipt={'source':video.name,'coverage_seconds':48,'sampling_fps':4,'model':model,'cleanup':False}
try:
    uploaded=client.files.upload(file=str(video))
    deadline=time.monotonic()+180
    while uploaded.state.name!='ACTIVE':
        if uploaded.state.name=='FAILED':raise RuntimeError('Video processing failed')
        if time.monotonic()>deadline:raise TimeoutError('Video processing timeout')
        time.sleep(3);uploaded=client.files.get(name=uploaded.name)
    response=client.models.generate_content(model=model,contents=[types.Part(file_data=types.FileData(file_uri=uploaded.uri,mime_type='video/mp4'),video_metadata=types.VideoMetadata(fps=4)),
        'Review actual whole 48-second map animation. Four semitrailer trucks red/blue/green/yellow are intentional. Focus on visible motion: count, disappearing/duplicated trucks, coherent cab/trailer coupling at turns, obvious intersections between trucks, clipping into illustrated buildings, flicker, and loop-end versus start. Cite timestamps HH:MM:SS for any observation. Distinguish observed defects from interpretation and uncertainty. Do not infer cabin occupancy from roofs/rear or invent unseen passengers. This is a candidate, not final art. Existing trajectories retained; do not judge user interface, absent from video. Return concise Russian under450words, covered interval, evidence, limitations.'],config=types.GenerateContentConfig(temperature=.1,max_output_tokens=2500,thinking_config=types.ThinkingConfig(thinking_budget=512)))
    (P/'video-v07-review.md').write_text(response.text or '')
    receipt['usage']=response.usage_metadata.model_dump(mode='json')
finally:
    if uploaded:client.files.delete(name=uploaded.name);receipt['cleanup']=True
    (P/'video-v07-review-receipt.json').write_text(json.dumps(receipt,indent=2))
print('Video analysis saved; uploaded copy removed')
