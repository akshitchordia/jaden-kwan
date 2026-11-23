"""FCP7 XML (xmeml v4) for Premiere: V1 talking head, V2 B-rolls, A1/A2 mix. No captions."""
import json
from urllib.parse import quote
from xml.sax.saxutils import escape
N = 1265  # sequence length in frames (23.976)
ROOT = 'C:/Video editor/14th nov/'
meta = json.load(open('/home/claude/sb3/premiere/clips.json'))

def url(p): return 'file://localhost/' + quote(p, safe='/:')
RATE = '<rate><timebase>24</timebase><ntsc>TRUE</ntsc></rate>'

def vfile(fid, name, path, dur, audio=False):
    au = ('<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics>'
          '<channelcount>2</channelcount></audio>') if audio else ''
    return (f'<file id="{fid}"><name>{escape(name)}</name><pathurl>{url(path)}</pathurl>{RATE}<duration>{dur}</duration>'
            f'<timecode>{RATE}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>'
            f'<media><video><samplecharacteristics>{RATE}<width>1080</width><height>1920</height>'
            f'<anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance>'
            f'</samplecharacteristics></video>{au}</media></file>')

def vclip(cid, name, fid_xml, start, dur, src_in=0):
    return (f'<clipitem id="{cid}"><name>{escape(name)}</name><enabled>TRUE</enabled><duration>{dur}</duration>{RATE}'
            f'<start>{start}</start><end>{start + dur}</end><in>{src_in}</in><out>{src_in + dur}</out>'
            f'<pixelaspectratio>square</pixelaspectratio>{fid_xml}</clipitem>')

def aclip(cid, name, fid_xml, start, dur, ch):
    return (f'<clipitem id="{cid}"><name>{escape(name)}</name><enabled>TRUE</enabled><duration>{dur}</duration>{RATE}'
            f'<start>{start}</start><end>{start + dur}</end><in>0</in><out>{dur}</out>{fid_xml}'
            f'<sourcetrack><mediatype>audio</mediatype><trackindex>{ch}</trackindex></sourcetrack></clipitem>')

# V1: the locked talking-head cut (its own audio stays unused; the mix sits on A1/A2)
v1 = vclip('clipitem-th', 'Fridge_zoom_v2_tight', vfile('file-th', 'Fridge_zoom_v2_tight.mp4', ROOT + 'Fridge_zoom_v2_tight.mp4', N, True), 0, N)
# V2: B-rolls
v2 = []
for k, (name, m) in enumerate(sorted(meta.items(), key=lambda kv: kv[1]['start'])):
    fx = vfile(f'file-b{k}', name + '.mp4', ROOT + 'premiere/broll/' + name + '.mp4', m['frames'])
    v2.append(vclip(f'clipitem-b{k}', name, fx, m['start'], m['frames']))
# A1/A2: the mix wav, stereo split across two tracks
wav = ('<file id="file-mix"><name>Fridge_zoom_v2_mix.wav</name><pathurl>' + url(ROOT + 'Fridge_zoom_v2_mix.wav') + f'</pathurl>{RATE}'
       f'<duration>{N}</duration><media><audio><samplecharacteristics><depth>24</depth><samplerate>48000</samplerate>'
       '</samplecharacteristics><channelcount>2</channelcount></audio></media></file>')
a1 = aclip('clipitem-a1', 'Fridge_zoom_v2_mix', wav, 0, N, 1)
a2 = aclip('clipitem-a2', 'Fridge_zoom_v2_mix', '<file id="file-mix"/>', 0, N, 2)

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="seq-fridge">'
       f'<name>Fridge v3 - talking head + B-roll layers</name><duration>{N}</duration>{RATE}'
       f'<timecode>{RATE}<string>00:00:00:00</string><frame>0</frame><displayformat>NDF</displayformat></timecode>'
       '<media><video><format><samplecharacteristics>' + RATE +
       '<width>1080</width><height>1920</height><anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio>'
       '<fielddominance>none</fielddominance></samplecharacteristics></format>'
       f'<track><enabled>TRUE</enabled><locked>FALSE</locked>{v1}</track>'
       f'<track><enabled>TRUE</enabled><locked>FALSE</locked>{"".join(v2)}</track></video>'
       '<audio><numOutputChannels>2</numOutputChannels>'
       '<format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format>'
       f'<track><enabled>TRUE</enabled><locked>FALSE</locked>{a1}<outputchannelindex>1</outputchannelindex></track>'
       f'<track><enabled>TRUE</enabled><locked>FALSE</locked>{a2}<outputchannelindex>2</outputchannelindex></track>'
       '</audio></media></sequence></xmeml>\n')
open('/home/claude/sb3/premiere/Fridge_v3_broll_layers.xml', 'w', encoding='utf-8').write(xml)
print('clips on V2:', len(v2))
