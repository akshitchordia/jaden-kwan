import sys, subprocess, numpy as np
which=sys.argv[1]; out=sys.argv[2]; sys.argv=[sys.argv[0],'x']
W,H=1080,1920
if which=='open':
    exec(open('open_anim.py').read().split("if __name__ == '__main__':")[0]); frames=range(F_IN,F_OUT); fn=lambda n: anim_frame(n/FPS,n)
else:
    exec(open('clients_anim.py').read().split("if __name__ == '__main__':")[0]); frames=range(189,262); fn=lambda n: render(n/FPS,n)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24000/1001','-i','-','-c:v','libx264','-crf','12','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',out],stdin=subprocess.PIPE)
for n in frames: enc.stdin.write((fn(n)*255+0.5).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print(which, len(frames), 'frames', frames[0], frames[-1])
