"""Check the production-root files, not only Astro's source or docs output."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import subprocess, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
ROUTES=['music-mirror/index.html','music-mirror/get-started/index.html','music-mirror/faq/index.html','music-mirror/support.html','music-mirror/privacy.html']
STORE='https://apps.apple.com/us/app/music-mirror/id6762572883'
class Page(HTMLParser):
 def __init__(self, text):
  super().__init__();self.tags=[];self.ids=set();self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if 'id' in a: self.ids.add(a['id'])
errors=[];checked=0;results=[]
for route in ROUTES:
 p=ROOT/route; text=p.read_text();page=Page(text)
 assert p.read_bytes()==(ROOT/'docs'/route).read_bytes(),f'Root/docs mismatch: {route}'
 if route.endswith('privacy.html'):
  before=subprocess.check_output(['git','show','origin/main:music-mirror/privacy.html'],cwd=ROOT)
  assert p.read_bytes()==before,'Existing privacy text modified'
 else:
  assert sum(t=='h1' for t,a in page.tags)==1,route
  assert any(t=='a' and a.get('href')=='#main' for t,a in page.tags),route
  canonical='https://xinyuzhang.me/'+route.replace('index.html','')
  assert any(t=='link' and a.get('rel')=='canonical' and a.get('href')==canonical for t,a in page.tags),route
  assert not any(t in ['script','iframe','form'] for t,a in page.tags),route
  assert 'upcoming-preview' not in text and 'IN DEVELOPMENT' not in text,route
 for tag,attrs in page.tags:
  if tag=='img': assert 'alt' in attrs and attrs.get('width') and attrs.get('height'),route
  for attr in ['href','src']:
   href=attrs.get(attr)
   if not href: continue
   url=urlsplit(href)
   if url.scheme in ['https','http','mailto']:
    if 'apps.apple.com' in href: assert href==STORE,href
    if url.scheme=='mailto': assert url.path=='musicmirror@xinyuzhang.me',href
    if attr=='src': errors.append(f'External initial resource: {href}')
    continue
   dest=ROOT/url.path.lstrip('/') if url.path.startswith('/') else p.parent/url.path
   if not url.path: dest=p
   if dest.is_dir():dest/= 'index.html'
   if not dest.exists(): errors.append(f'{route}: missing {href}')
   elif url.fragment and dest.suffix=='.html' and unquote(url.fragment) not in Page(dest.read_text()).ids:errors.append(f'{route}: missing anchor {href}')
   checked+=1
 results.append({'route':route,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
# These unrelated files must remain identical to the publication branch.
for route in ['index.html','blog/index.html','CNAME','.nojekyll','docs/index.html','docs/blog/index.html']:
 assert (ROOT/route).read_bytes()==subprocess.check_output(['git','show','origin/main:'+route],cwd=ROOT),f'Unrelated change: {route}'
assert not errors, '\n'.join(errors)
print(json.dumps({'status':'passed','local_links_and_resources_checked':checked,'pages':results,'privacy':'byte-identical to origin/main','unrelated_site_files':'unchanged','browser_QA':'not covered by static checks'},indent=2))
