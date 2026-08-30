#!/usr/bin/env python3
"""Debug gdflix with cloudscraper."""
from cloudscraper import create_scraper
from lxml.etree import HTML
from re import findall
from urllib.parse import parse_qs, urlparse

url = "https://new3.gdflix.io/file/mupwL2bGynLxtC5"

scraper = create_scraper()
scraper.headers.update({
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    'referer': url,
})

resp = scraper.get(url, timeout=30)
print(f"Status: {resp.status_code}")
print(f"Content length: {len(resp.text)}")
print(f"Has busycdn: {'instant.busycdn' in resp.text}")

html = HTML(resp.content)
busycdn_links = html.xpath('//a[contains(@href,"instant.busycdn")]/@href')
print(f"Busycdn links: {len(busycdn_links)}")

if busycdn_links:
    busycdn_url = busycdn_links[0]
    print(f"Busycdn URL: {busycdn_url[:80]}...")
    
    resp2 = scraper.get(busycdn_url, allow_redirects=False, timeout=30)
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

# Also check API
key_match = findall(r'key",\s*"([a-f0-9]{30,})"', resp.text)
print(f"\nKey found: {key_match}")
if key_match:
    key = key_match[0]
    resp3 = scraper.post(url, data={
        'action': 'direct',
        'key': key,
        'action_token': '',
    }, headers={'x-token': 'new3.gdflix.io'}, timeout=30)
    print(f"API direct: {resp3.text[:200]}")