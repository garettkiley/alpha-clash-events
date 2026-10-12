"""Hourly fetch of every Alpha Clash event on XP Network -> events.json
Primary: activity (game) filter  activities=6 (Alpha Clash), 394 (Cosmic Conquest), 395 (Siege of the Forgotten).
Fallback/union: text query 'alpha clash'. Paginated with limit=30 (API max) + offset. De-duplicated by id. Test events dropped."""
import json,urllib.request,urllib.parse,time,re,datetime
API='https://api.xpnetwork.com/search/events'
ACTS={6:'Alpha Clash',394:'Cosmic Conquest',395:'Siege of the Forgotten'}
def get(params):
    out=[];off=0
    while off<5000:
        q=urllib.parse.urlencode(dict(params,limit=30,offset=off))
        for t in range(3):
            try:
                d=json.load(urllib.request.urlopen(urllib.request.Request(f'{API}?{q}',headers={'User-Agent':'alpha-clash-events (github.com/garettkiley/alpha-clash-events)'}),timeout=30));break
            except Exception as e:
                if t==2: raise
                time.sleep(5)
        if not isinstance(d,list) or not d: break
        out+=d; off+=len(d)
        if len(d)<30: break
        time.sleep(.3)
    return out
TEST=re.compile(r'\b(test|testing|dummy|do not join|ignore)\b',re.I)
def main():
    U={};src={}
    for a in ACTS:
        for e in get({'activities':a}): U[e['id']]=e; src.setdefault(e['id'],set()).add(f'activity:{a}')
    for e in get({'query':'alpha clash'}):
        names={x['id'] for x in e.get('activities',[])}
        if names & set(ACTS) or 'alpha clash' in (e.get('title','')+' '+(e.get('description') or '')).lower():
            U.setdefault(e['id'],e); src.setdefault(e['id'],set()).add('query')
    ev=[]
    for e in U.values():
        if e.get('private') or e.get('status')!='published' or TEST.search(e.get('title') or ''): continue
        loc=e.get('physical_location') or {}
        ev.append({'id':e['id'],'title':e['title'].strip(),'start':e['start_date'],'end':e.get('end_date'),'timezone':e.get('timezone'),
          'type':e.get('event_type'),'location_type':e.get('location_type'),'store':loc.get('name'),'address':loc.get('formatted_address'),
          'city_state':', '.join(x for x in [loc.get('state'),loc.get('country')] if x),'lat':loc.get('latitude'),'lng':loc.get('longitude'),
          'games':[a['name'] for a in e.get('activities',[]) if a['id'] in ACTS] or ['Alpha Clash'],
          'image':e.get('search_preview_image'),'cost':e.get('cost'),'currency':e.get('currency_code'),'capacity':e.get('capacity'),
          'url':f"https://xpnetwork.com/events/{e["id"]}/details"})
    ev.sort(key=lambda x:x['start'])
    json.dump({'generated':datetime.datetime.now(datetime.UTC).replace(tzinfo=None).replace(microsecond=0).isoformat()+'Z','source':'api.xpnetwork.com/search/events',
      'method':'activities=6,394,395 union query=alpha clash; limit=30 offset pagination; dedup by id; private/unpublished/test removed',
      'count':len(ev),'events':ev},open('events.json','w'),indent=1)
    print(len(U),'raw ->',len(ev),'events')
if __name__=='__main__': main()
