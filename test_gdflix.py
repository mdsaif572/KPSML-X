#!/usr/bin/env python3
"""Test gdflix direct link generator."""
import sys
import os

# Set minimal env vars
os.environ['BOT_TOKEN'] = '123:abc'
os.environ['OWNER_ID'] = '123'
os.environ['TELEGRAM_API'] = '123'
os.environ['TELEGRAM_HASH'] = 'testhash'
os.environ['PORT'] = '8080'

sys.path.insert(0, '.')

# Import gdflix function directly without triggering bot.__init__
import importlib.util

# Load the module directly
spec = importlib.util.spec_from_file_location(
    "direct_link_generator",
    "bot/helper/mirror_utils/download_utils/direct_link_generator.py"
)
# We can't load it directly because it imports from bot.* 
# So let's test the gdflix function logic standalone

import requests
from lxml.etree import HTML
from re import findall
from urllib.parse import parse_qs, urlparse

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
url = "https://new3.gdflix.io/file/mupwL2bGynLxtC5"

session = requests.Session()
session.headers.update({
    'user-agent': user_agent,
    'referer': url,
})

print("Fetching GDFlix page...")
resp = session.get(url, timeout=30)
html = HTML(resp.content)

# Method 1: Extract instant download link (busycdn) from HTML
busycdn_links = html.xpath('//a[contains(@href,"instant.busycdn")]/@href')
print(f"Found {len(busycdn_links)} busycdn links")

if busycdn_links:
    busycdn_url = busycdn_links[0]
    print(f"Busycdn URL: {busycdn_url[:80]}...")
    
    resp2 = session.get(busycdn_url, allow_redirects=False, timeout=30)
    print(f"Busycdn status: {resp2.status_code}")
    
    if resp2.status_code == 302:
        location = resp2.headers.get('location', '')
        print(f"Redirect to: {location[:100]}...")
        
        parsed = urlparse(location)
        qs = parse_qs(parsed.query)
        direct_url = qs.get('url', [None])[0]
        
        if direct_url:
            name = direct_url.split('/')[-1].split('?')[0] if '?' in direct_url else direct_url.split('/')[-1]
            final = f"{direct_url}#{name}" if name else direct_url
            print(f"\n✅ SUCCESS! Direct download link:")
            print(f"   URL: {direct_url[:100]}...")
            print(f"   Name: {name}")
            print(f"   Full: {final[:120]}...")
        else:
            print(f"❌ No 'url' param in redirect location")
            print(f"   Returning location: {location}")
    else:
        print(f"❌ Unexpected status: {resp2.status_code}")
else:
    print("❌ No busycdn links found, trying API...")

# Method 2: API
key_match = findall(r'key",\s*"([a-f0-9]{30,})"', resp.text)
if key_match:
    key = key_match[0]
    print(f"\nFound key: {key}")
    
    resp3 = session.post(url, data={
        'action': 'direct',
        'key': key,
        'action_token': '',
    }, headers={'x-token': urlparse(url).hostname or ''}, timeout=30)
    print(f"API direct response: {resp3.text}")