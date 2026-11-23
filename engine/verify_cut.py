"""Check a rendered first cut: re-transcribe, longest pause between words, word count vs the master, frame count.
Usage: python verify_cut.py <firstcut.mp4> <words_master.json> <out_report.json>"""
import sys, json, subprocess, os, tempfile
import config as C
from transcribe import transcribe

def main(mp4, master_words, out):
    tmp = os.path.join(tempfile.gettempdir(), 'verify_16k.wav')
    subprocess.run([C.FFMPEG, '-v', 'error', '-y', '-i', mp4, '-ac', '1', '-ar', '16000', tmp], check=True)
    ws = transcribe(tmp, tmp + '.json')
    gaps = sorted(((b['s'] - a['e']), a['w'], b['w'], round(a['e'], 2)) for a, b in zip(ws, ws[1:]))[::-1]
    mw = json.load(open(master_words, encoding='utf-8'))['words']
    n = subprocess.run([C.FFPROBE, '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets',
                        '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout.strip()
    rep = dict(frames=int(n), words_master=len(mw), words_cut=len(ws),
               longest_pauses=[dict(gap=round(g, 2), between=f'{a} | {b}', at=t) for g, a, b, t in gaps[:6]])
    json.dump(rep, open(out, 'w', encoding='utf-8'), indent=1)
    print(json.dumps(rep, indent=1))

if __name__ == '__main__':
    main(*sys.argv[1:4])
