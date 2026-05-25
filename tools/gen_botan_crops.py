#!/usr/bin/env python3
"""Regenerate per-code Botan crop PNGs from the embedded data in fx-code-search.html.
Crops are written to /tmp/botan/crops/<code>.png. Used to OCR Botan family content
into text (botan_text.json). Resumable: skips codes already present in botan_text.json.
"""
import re, json, base64, io, os
from PIL import Image

HTML = 'fx-code-search.html'

def grab(name, html):
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % name, html, re.S)
    return json.loads(m.group(1))

def main():
    html = open(HTML, encoding='utf-8', errors='replace').read()
    crops = grab('botanCrops', html)
    pages = grab('botanPages', html)
    idxlist = grab('botanCodeIndex', html)
    os.makedirs('/tmp/botan/crops', exist_ok=True)
    cache = {}
    def page_img(p):
        if p not in cache:
            cache[p] = Image.open(io.BytesIO(base64.b64decode(pages[p]))).convert('RGB')
        return cache[p]
    order = []
    for e in idxlist:
        c = e['code']
        if c not in crops:
            continue
        cr = crops[c]
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
