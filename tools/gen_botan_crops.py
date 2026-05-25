#!/usr/bin/env python3
"""Regenerate per-code Botan crop PNGs from FX_코드조회.html embedded data.

The newer file stores its index/crops as gzip+base64 (script type="text/plain"),
while botanPages is plain JSON. Crops are written to /tmp/botan/crops/<code>.png
and the ordered code list to /tmp/botan/order.json.

Used to OCR the Botan family manual content into clean text (botan_text.json),
which is then re-compressed and injected back into the botanText block.
"""
import re, json, base64, gzip, io, os
from PIL import Image

HTML = 'FX_코드조회.html'


def block(html, name):
    m = re.search(r'<script[^>]*id="%s">(.*?)</script>' % name, html, re.S)
    return m.group(1).strip()


def gz_json(html, name):
    return json.loads(gzip.decompress(base64.b64decode(block(html, name))).decode('utf-8'))


def plain_json(html, name):
    return json.loads(block(html, name))


def main():
    html = open(HTML, encoding='utf-8', errors='replace').read()
    crops = gz_json(html, 'botanCrops')
    idxlist = gz_json(html, 'botanCodeIndex')
    pages = plain_json(html, 'botanPages')

    os.makedirs('/tmp/botan/crops', exist_ok=True)
    cache = {}

    def page_img(p):
        if p not in cache:
            cache[p] = Image.open(io.BytesIO(base64.b64decode(pages[p]))).convert('RGB')
        return cache[p]

    order = []
    for e in idxlist:
        c = e['code']
        cr = crops.get(c) or crops.get(c.lower())
        if not cr:
            continue
        im = page_img(str(cr['page']))
        cim = im.crop((cr['x'], cr['y'], cr['x'] + cr['w'], cr['y'] + cr['h']))
        if cim.width > 900:
            r = 900 / cim.width
            cim = cim.resize((900, max(1, int(cim.height * r))))
        cim.save(f'/tmp/botan/crops/{c}.png')
        order.append(c)
    json.dump(order, open('/tmp/botan/order.json', 'w'))
    print('generated crops:', len(order))


if __name__ == '__main__':
    main()
