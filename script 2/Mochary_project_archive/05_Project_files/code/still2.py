import sys,numpy as np,cv2
exec(open('clients_anim.py').read().split("if __name__ == '__main__':")[0])
tiles=[]
for t in [7.89,7.95,8.05,8.25,8.5,8.80,8.86,8.95,9.2,9.6,9.82,9.9,10.1,10.5,10.85]:
    fr=render(t,int(t*FPS)); im=cv2.resize((fr[...,::-1]*255).astype(np.uint8),(270,480)); cv2.putText(im,f'{t}',(4,18),0,0.55,(0,255,255),1); tiles.append(im)
cv2.imwrite('cl_still.jpg',np.vstack([np.hstack(tiles[i:i+8]) for i in range(0,16,8)]) if len(tiles)==16 else np.vstack([np.hstack(tiles[0:8]),np.hstack(tiles[8:15]+[np.zeros_like(tiles[0])])]))
