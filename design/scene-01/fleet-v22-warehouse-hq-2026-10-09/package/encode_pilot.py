from compose import *
out=P/'quality-pilot-4s.mp4'
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','3840x2668','-r','24','-i','-','-an','-c:v','libx264','-preset','slow','-crf','15','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
for f in range(1,97):
 proc.stdin.write(compose(f).tobytes())
proc.stdin.close();assert proc.wait()==0
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-frames:v','1',str(P/'pilot-decoded.png')],check=True)
a=np.asarray(compose(1),dtype=np.float32);b=np.asarray(Image.open(P/'pilot-decoded.png').convert('RGB'),dtype=np.float32)
mse=float(np.mean((a-b)**2));psnr=float(10*np.log10(255**2/mse))
(P/'pilot-codec-quality.json').write_text(json.dumps({'codec':'H264 CRF15 slow yuv420p','decoded_width':b.shape[1],'decoded_height':b.shape[0],'first_frame_psnr_vs_composite_db':psnr,'scope':'codec distortion only, not ground-truth source detail'},indent=2));print('PILOT_CODEC_PSNR',psnr)
