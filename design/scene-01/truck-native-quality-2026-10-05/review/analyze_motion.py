import os
import pathlib
import time
import json
from google import genai
from google.genai import types

P=pathlib.Path(__file__).resolve().parent
video=P.parent/'image-to-3d/motion/green-tractor-turn-detailed.mp4'
assert video.exists()
key=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
assert key, 'Gemini private configuration missing'
client=genai.Client(api_key=key)
uploaded=None
receipt={'uploaded_video':video.name,'coverage_seconds':6,'cleanup':False}
try:
    uploaded=client.files.upload(file=str(video))
    deadline=time.monotonic()+120
    while uploaded.state.name != 'ACTIVE':
        if uploaded.state.name == 'FAILED': raise RuntimeError('Video processing failed')
        if time.monotonic()>deadline: raise TimeoutError('Video processing timeout')
        time.sleep(3)
        uploaded=client.files.get(name=uploaded.name)
    response=client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[types.Part(file_data=types.FileData(file_uri=uploaded.uri,mime_type='video/mp4'), video_metadata=types.VideoMetadata(fps=8)),
            'Inspect the ACTUAL entire 6-second video as a skeptical vehicle-animation reviewer. This is an isolated engineering prototype on a pale blue background, not finished map art. Cite timestamps. Does the tractor TRANSLATE through a 90-degree turn with a physically understandable attached articulated semitrailer, or rotate around a stationary centre? Does the white trailer follow and align on exit? Check count, duplicate/deforming vehicle, collision/disconnection, cropping, tyre rotation, flicker and abrupt texture changes. Are two adults distinguishable in the green cab whenever its FRONT windshield is visible (not from rear)? Separate observable evidence from interpretation. Return concise text under 650 words, explicit pass/fail for MOTION and separate art/detail caveats. Do not overlook missing tyre rotation or flat portrait textures.'],
        config=types.GenerateContentConfig(temperature=0.1,max_output_tokens=3500,thinking_config=types.ThinkingConfig(thinking_budget=512)))
    (P/'motion-gemini-review.md').write_text(response.text or '')
    receipt['model']='gemini-2.5-flash'
finally:
    if uploaded:
        client.files.delete(name=uploaded.name)
        receipt['cleanup']=True
    (P/'motion-analysis-receipt.json').write_text(json.dumps(receipt,indent=2))
print('Actual video reviewed; uploaded copy deleted')
