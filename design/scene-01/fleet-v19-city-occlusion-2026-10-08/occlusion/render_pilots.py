import bpy,json,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'after'
frames=[int(x) for x in args[1:]] or [150,154,158]
s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
s.render.use_compositing=False
dest=P/mode;dest.mkdir(exist_ok=True)
for f in frames:
 s.frame_set(f);s.render.filepath=str(dest/f'{f:04}.png');t=time.monotonic();bpy.ops.render.render(write_still=True);print('FRAME',mode,f,time.monotonic()-t,flush=True)
