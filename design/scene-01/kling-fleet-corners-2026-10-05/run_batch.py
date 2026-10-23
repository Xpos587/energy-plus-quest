import subprocess,json,time,urllib.request,concurrent.futures
from pathlib import Path
p=Path(__file__).resolve().parent
segments=[('0-1','0','1','full','Start facing UP. Drive forward north along the starting vertical blue street, make ONE broad left turn on the upper horizontal street. Finish facing LEFT at the precise supplied end location. Cab leads; trailer follows the inner arc.'),('1-mid','1','1p5-local-repair','crop','ONLY FIRST HALF of left-to-down corner. Start cab facing LEFT. Drive a SHORT distance left toward the junction then steer diagonally DOWN-LEFT. Finish exactly at supplied bent midpoint: cab DOWN-LEFT, trailer still behind toward RIGHT. Do NOT complete the turn, do NOT continue west out of crop.'),('mid-2','1p5-local-repair','2-local-repair','crop','ONLY SECOND HALF of left-to-down corner. Start supplied bent midpoint: cab DOWN-LEFT, trailer trailing toward RIGHT. Continue FORWARD, smoothly complete steering DOWN and proceed south along this vertical street. Finish facing DOWN at precise supplied end location. Trailer swings inside coupled hitch; no reversing or U-turn.'),('2-3','2-local-repair','3','full','Start facing DOWN. Drive forward south along the starting vertical street, make ONE broad left turn into the lower horizontal blue street, continue RIGHT. Finish facing RIGHT at exact supplied end location. Cab leads and trailer follows the inner arc.'),('3-0','3','0','full','Start facing RIGHT. Drive forward east along the starting lower horizontal street, make ONE broad left turn into starting eastern vertical blue street, proceed UP. Finish facing UP at exact supplied end location, smoothly completing this route quarter. Cab leads, no reversing.')]
receipts=[];start=time.monotonic()
def run(color,seg):
 label,a,b,mode,motion=seg;name=f'{color}-{label}';suffix='-crop-padded.png' if mode=='crop' else '-padded.png'
 first=p/f'{color}-key-{a}{suffix}';last=p/f'{color}-key-{b}{suffix}'
 prompt=f'Locked aerial camera and fixed clean bright 2D illustrated city. Exactly ONE {color.upper()} tractor connected to ONE rigid cream tarp semitrailer. Same cab and attached trailer as supplied keys, preserve scale, structural identity, wheels, detailed grille and mirrors. EXACTLY ONE adult driver, empty passenger seat; no second human, no head duplication. ONLY forward motion, CAB ALWAYS LEADING. Single connected articulated rig, fifth-wheel coupling stays attached; trailer rear axle follows inner curve. No swapping ends, no reverse, no U-turn, no duplicates, no morphing, no disappearance, no roof crossing. Entire rig stays on BLUE ASPHALT inside visible city crop, NEVER enters white padding. City/background/camera/lighting totally locked and unchanged; bright cream/apricot buildings, powder-blue roads, soft colored contours and contact shadows, no black outlines or grey veil. Five second continuous SILENT shot. Required exact first and last supplied poses. {motion}'
 (p/f'{name}-prompt.txt').write_text(prompt)
 cmd=['higgsfield','generate','create','kling3_0','--prompt',prompt,'--start-image',str(first),'--end-image',str(last),'--duration','5','--mode','std','--sound','off','--aspect_ratio','16:9','--wait','--wait-timeout','20m','--wait-interval','5s','--json']
 t=time.monotonic();r={'name':name,'crop_mode':mode,'start_input':first.name,'end_input':last.name,'status':'submitting','prompt_file':f'{name}-prompt.txt'}
 (p/f'{name}-status.json').write_text(json.dumps(r,indent=2));print('START',name,flush=True)
 completed=subprocess.run(cmd,text=True,capture_output=True)
 (p/f'{name}-result.json').write_text(completed.stdout);(p/f'{name}-stderr.log').write_text(completed.stderr)
 r.update(returncode=completed.returncode,measured_job_elapsed_seconds=round(time.monotonic()-t,3))
 try:
  data=json.loads(completed.stdout);jobs=data if isinstance(data,list) else [data];job=jobs[0];r.update(job_id=job.get('id'),provider_status=job.get('status'),result_url=job.get('result_url'))
  if completed.returncode or job.get('status')!='completed' or not job.get('result_url'):raise RuntimeError('provider did not return completed media')
  video=p/f'{name}.mp4';urllib.request.urlretrieve(job['result_url'],video)
  probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate,codec_type','-of','json',str(video)],text=True,capture_output=True,check=True);metadata=json.loads(probe.stdout);(p/f'{name}-media.json').write_text(json.dumps(metadata,indent=2));r.update(status='downloaded',media_file=video.name,actual_duration_seconds=float(metadata['format']['duration']))
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),'-vf',"fps=4,scale=384:-1,drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=18:fontcolor=black:box=1:boxcolor=white@0.8,tile=5x4",'-frames:v','1',str(p/f'{name}-quarter-second-contact.png')],check=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-sseof','-0.05','-i',str(video),'-frames:v','1',str(p/f'{name}-end.png')],check=True)
  r['contact_sheet']=f'{name}-quarter-second-contact.png'
 except Exception as e:
  r.update(status='needs_inspection',error=str(e))
  # Unknown outcomes are inspected once, never blindly duplicated.
  recent=subprocess.run(['higgsfield','generate','list','--video','--size','50','--json'],text=True,capture_output=True);(p/f'{name}-recent-jobs.json').write_text(recent.stdout)
 (p/f'{name}-status.json').write_text(json.dumps(r,indent=2));print('END',name,r['status'],r.get('job_id'),flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for color in ('red','yellow'):
  futures=[pool.submit(run,color,seg) for seg in segments]
  for future in concurrent.futures.as_completed(futures):
   receipts.append(future.result());(p/'batch-progress.json').write_text(json.dumps({'completed_commands':len(receipts),'required_commands':10,'results':receipts,'elapsed_seconds':round(time.monotonic()-start,3),'review_pass_claimed':False},indent=2))
(p/'completion-receipt.json').write_text(json.dumps({'results':receipts,'measured_batch_elapsed_seconds':round(time.monotonic()-start,3),'review_pass_claimed':False,'crop_geometry':[420,460,700,100],'padding':[1920,1080],'model':'kling3_0','mode':'std','sound':'off','requested_duration_seconds':5,'duplicate_retries':0},indent=2))
print('BATCH COMPLETE',flush=True)
