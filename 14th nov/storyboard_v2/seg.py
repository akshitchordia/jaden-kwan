import onnxruntime as ort, numpy as np, cv2
_s=None
def matte(img_rgb):
    """u2net_human_seg alpha (0..1) at image size; img float 0..1 RGB"""
    global _s
    if _s is None: _s=ort.InferenceSession('/home/claude/u2net_human_seg.onnx',providers=['CPUExecutionProvider'])
    h,w=img_rgb.shape[:2]
    x=cv2.resize(img_rgb,(320,320),interpolation=cv2.INTER_AREA).astype(np.float32)
    x=(x-np.array([0.485,0.456,0.406]))/np.array([0.229,0.224,0.225])
    x=x.transpose(2,0,1)[None].astype(np.float32)
    o=_s.run(None,{_s.get_inputs()[0].name:x})[0][0,0]
    o=(o-o.min())/(o.max()-o.min()+1e-6)
    a=cv2.resize(o,(w,h),interpolation=cv2.INTER_CUBIC)
    a=np.clip((a-0.15)/0.7,0,1)
    return cv2.GaussianBlur(a,(0,0),1.2)
