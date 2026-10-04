"""Sonda: quali dati meteo sono disponibili per l'Islanda (solo diagnostica)."""
import json, urllib.request, datetime as dt

def get(url, n=700):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'islanda-2026-ricerca'})
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read().decode('utf-8', 'replace')
        print(f'OK {url}\n   {body[:n]!r}\n')
        return body
    except Exception as e:
        print(f'ERR {url}\n   {e}\n')

VIK = (63.4186, -19.0060)
V = 'cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high'
for m in ['best_match', 'dmi_seamless', 'dmi_harmonie_arome_europe', 'metno_seamless', 'icon_seamless',
          'ecmwf_ifs025', 'ukmo_seamless', 'knmi_seamless', 'meteofrance_seamless', 'gfs_seamless']:
    b = get(f'https://api.open-meteo.com/v1/forecast?latitude={VIK[0]}&longitude={VIK[1]}&hourly={V}&models={m}&timezone=UTC&forecast_days=3', 120)
    if b:
        h = json.loads(b).get('hourly', {})
        for k in V.split(','):
            vals = h.get(k) or []
            print(f'   {m:28s} {k:18s} non-null {sum(v is not None for v in vals)}/{len(vals)} sample {vals[18:24]}')
        print()

get(f'https://previous-runs-api.open-meteo.com/v1/forecast?latitude={VIK[0]}&longitude={VIK[1]}&hourly=cloud_cover,cloud_cover_previous_day1,cloud_cover_low_previous_day1&models=dmi_seamless&past_days=7&forecast_days=1&timezone=UTC', 900)
d0 = (dt.date.today() - dt.timedelta(days=20)).isoformat(); d1 = (dt.date.today() - dt.timedelta(days=1)).isoformat()
get(f'https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={VIK[0]}&longitude={VIK[1]}&hourly={V}&models=dmi_seamless&start_date={d0}&end_date={d1}&timezone=UTC', 600)
get(f'https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={VIK[0]}&longitude={VIK[1]}&hourly={V}&start_date={d0}&end_date={d1}&timezone=UTC', 600)

for st in ['BIRK', 'BIKF', 'BIVM']:
    get(f'https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station={st}&data=skyc1&data=skyl1&data=skyc2&data=skyl2&data=skyc3&data=skyl3&data=metar&year1=2026&month1=9&day1=28&year2=2026&month2=9&day2=29&tz=Etc/UTC&format=onlycomma&latlon=no&missing=M&trace=T&direct=no&report_type=3&report_type=4', 900)
get('https://www.ogimet.com/cgi-bin/getsynop?block=04&begin=202609280000&end=202609280600', 1500)
get('https://xmlweather.vedur.is/?op_w=xml&type=obs&lang=en&view=xml&ids=1;6015;6222;36308;6419&params=N;T;W', 1500)
