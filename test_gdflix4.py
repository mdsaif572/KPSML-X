#!/usr/bin/env python3
"""Debug gdflix with curl_cffi (impersonate browser TLS)."""
from curl_cffi import requests as cf_requests
from lxml.etree import HTML
from re import findall
from urllib.parse import parse_qs, urlparse

url = "https://new3.gdflix.io/file/mupwL2bGynLxtC5"

# curl_cffi impersonates real browser TLS fingerprint, bypassing Cloudflare
session = cf_requests.Session(impersonate="firefox")
session.headers.update({
    'referer': url,
})

resp = session.get(url, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Content length: {len(resp.text)}")
print(f"Has busycdn: {'instant.busycdn' in resp.text}")

html = HTML(resp.content)
busycdn_links = html.xpath('//a[contains(@href,"instant.busycdn")]/@href')
print(f"Busycdn links: {len(busycdn_links)}")

if busycdn_links:
    busycdn_url = busycdn_links[0]
    print(f"Busycdn URL: {busycdn_url[:80]}...")
    
    resp2 = session.get(busycdn_url, allow_redirects=False, timeout=30)
    print(f"Busycdn status: {resp2.status_code}")
    
    if resp2.status_code == 302:
        location = resp2.headers.get('location', '')
        print(f"Redirect: {location[:100]}...")
        
        parsed = urlparse(location)
        qs = parse_qs(parsed.query)
        direct_url = qs.get('url', [None])[0]
        
        if direct_url:
            name = direct_url.split('/')[-1].split('?')[0] if '?' in direct_url else direct_url.split('/')[-1]
            print(f"\n✅ Direct URL: {direct_url[:80]}...")
            print(f"   Name: {name}")
        else:
            print(f"   No url param, returning location: {location[:80]}")

# API test
key_match = findall(r'key",\s*"([a-f0-9]{30,})"', resp.text)
print(f"\nKey found: {key_match}")
if key_match:
    key = key_match[0]
    resp3 = session.post(url, data={
        'action': 'direct',
        'key': key,
        'action_token': '',
    }, headers={'x-token': 'new3.gdflix.io'}, timeout=30)
    print(f"API direct: {resp3.text[:200]}")