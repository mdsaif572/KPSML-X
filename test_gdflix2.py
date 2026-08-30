#!/usr/bin/env python3
"""Debug gdflix page fetch."""
import requests
from lxml.etree import HTML

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
url = "https://new3.gdflix.io/file/mupwL2bGynLxtC5"

session = requests.Session()
session.headers.update({
    'user-agent': user_agent,
    'referer': url,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
})

resp = session.get(url, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Content length: {len(resp.text)}")
print(f"Has busycdn: {'instant.busycdn' in resp.text}")

# Check if it's a cloudflare challenge page
if 'cf-challenge' in resp.text or 'cloudflare' in resp.text.lower() or 'turnstile' in resp.text.lower():
    print("Cloudflare challenge detected!")

html = HTML(resp.content)
links = html.xpath('//a/@href')
print(f"Total links found: {len(links)}")
for link in links:
    if 'busycdn' in link or 'download' in link.lower() or 'instant' in link:
        print(f"  -> {link[:100]}")

# Also check for the key
from re import findall
key_match = findall(r'key",\s*"([a-f0-9]{30,})"', resp.text)
print(f"Key found: {key_match}")

# Try API direct
if key_match:
    key = key_match[0]
    resp3 = session.post(url, data={
        'action': 'direct',
        'key': key,
        'action_token': '',
    }, headers={'x-token': 'new3.gdflix.io'}, timeout=30)
    print(f"API direct response: {resp3.text[:200]}")