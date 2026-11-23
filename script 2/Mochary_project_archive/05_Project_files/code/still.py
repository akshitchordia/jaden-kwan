import sys,numpy as np,cv2
sys.argv=['x','none']
exec(open('open_anim.py').read().split("if __name__ == '__main__':")[0])
tiles=[]
for t in [1.20,1.35,1.60,1.95,2.30,2.80,3.05,3.40,4.10,4.60,5.10,5.60,6.20,6.52,6.65,6.90,7.25]:
    fr=anim_frame(t,int(t*FPS)); im=cv2.resize((fr[...,::-1]*255).astype(np.uint8),(270,480)); cv2.putText(im,f'{t}',(4,18),0,0.55,(0,255,255),1); tiles.append(im)
while len(tiles)%9: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite('open_still.jpg',np.vstack([np.hstack(tiles[i:i+9]) for i in range(0,len(tiles),9)]))
