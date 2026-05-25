#!/usr/bin/env python3
"""Rebuild the botanText gzip+base64 block in FX_코드조회.html from botan_text.json.

botan_text.json maps: code -> {"title": str, "text": str}
Only codes with non-empty text are written into botanText; codes without text
fall back to the original manual page image (the app already supports this).

Re-runnable: run after adding more OCR entries to grow text coverage.
"""
import json, gzip, base64, re, sys

HTML = 'FX_코드조회.html'
SRC = 'botan_text.json'


def main():
    data = json.load(open(SRC, encoding='utf-8'))
    botan_text = {c: e['text'] for c, e in data.items() if e.get('text', '').strip()}

    payload = json.dumps(botan_text, ensure_ascii=False, separators=(',', ':'))
    b64 = base64.b64encode(gzip.compress(payload.encode('utf-8'), 9)).decode('ascii')

    html = open(HTML, encoding='utf-8').read()
    m = re.search(r'(<script[^>]*id="botanText">)(.*?)(</script>)', html, re.S)
    if not m:
        print('botanText block not found', file=sys.stderr)
        sys.exit(1)
    new_html = html[:m.start(2)] + b64 + html[m.end(2):]
    open(HTML, 'w', encoding='utf-8').write(new_html)

    # verify round-trip
    check = json.loads(gzip.decompress(base64.b64decode(b64)).decode('utf-8'))
    print(f'botanText entries written: {len(check)} (codes with text)')
    print(f'block base64 size: {len(b64)} bytes')


if __name__ == '__main__':
    main()
