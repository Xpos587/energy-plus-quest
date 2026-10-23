"""Serialize a Flowers media build with8192 assembly; no deploy or storage mutation."""
import argparse,fcntl,json,os,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def temp_path(value):
 p=(ROOT/value).resolve();p.relative_to((ROOT/'.tmp-work').resolve());return p
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build-dir',required=True);p.add_argument('--stage-dir',required=True);p.add_argument('--receipt',required=True);p.add_argument('--ui-snapshot');a=p.parse_args();build=temp_path(a.build_dir);stage=temp_path(a.stage_dir);bun=shutil.which('bun')
 if not bun:raise RuntimeError('bun unavailable')
 subprocess.run([bun,'scripts/repository-budget.ts','--local-only'],cwd=ROOT,check=True)
 lock_path=ROOT/'.tmp-work/flowers-global-assembly.lock';lock_path.parent.mkdir(exist_ok=True)
 with lock_path.open('a+')as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Assembly/media build resource slot busy; no build started')
  lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'operation':'media_build','buildDir':str(build.relative_to(ROOT))}));lock.flush();start=time.monotonic();env=os.environ.copy();env.update(BUILD_MINIFY='true',BUILD_SINGLEFILE='false',VIPS_CONCURRENCY='1')
  if a.ui_snapshot:env['FROZEN_UI_SOURCE_DIR']=str(temp_path(a.ui_snapshot))
  else:env['FROZEN_UI_CAPTURE_DIR']=str(ROOT/'.tmp-work/ui-source-snapshots'/build.name)
  subprocess.run([bun,'run','build:media'if a.ui_snapshot else'build:app','--outDir',str(build)],cwd=ROOT,env=env,check=True)
  subprocess.run([bun,'scripts/stage-static.mjs',str(build),str(stage),'deploy/nginx-joydelivery.conf'],cwd=ROOT,env=env,check=True)
  # Vite copies all public source masters into its output. The staged release
  # already contains the referenced files; keeping both created GiB per run.
  shutil.rmtree(build)
  subprocess.run([bun,'scripts/repository-budget.ts','--local-only'],cwd=ROOT,check=True)
  receipt={'status':'built_and_staged_runtime_verification_pending','buildDir':str(build.relative_to(ROOT)),'stageDir':str(stage.relative_to(ROOT)),'uiSnapshot':a.ui_snapshot or str(Path('.tmp-work/ui-source-snapshots')/build.name),'mediaOnly':bool(a.ui_snapshot),'wallSeconds':time.monotonic()-start,'childPeakRSSKiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'vipsConcurrency':1,'sharedResourceSlot':'flowers-global-assembly.lock','published':False,'storageModified':False};out=ROOT/a.receipt;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
