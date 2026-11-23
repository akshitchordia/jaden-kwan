"""Word-level transcription. Usage: python -I transcribe.py <audio_or_video> <out.json> [model]"""
import sys, json
from faster_whisper import WhisperModel

def transcribe(src, out, model_name='small.en'):
    model = WhisperModel(model_name, device='cpu', compute_type='int8')
    segs, info = model.transcribe(src, word_timestamps=True, vad_filter=False, beam_size=5)
    words = []
    for s in segs:
        for w in s.words:
            words.append({'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3), 'p': round(w.probability, 3)})
    json.dump({'duration': info.duration, 'words': words}, open(out, 'w', encoding='utf-8'), indent=1)
    return words

if __name__ == '__main__':
    ws = transcribe(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'small.en')
    print(len(ws), 'words')
