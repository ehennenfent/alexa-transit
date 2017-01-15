import requests, json
from stops import stops_m
stops = {}
for stop in stops_m:
    try:
        stops[stop.lower()] = stops_m[stop]
    except KeyError:
        pass

# Don't commit API keys, I know. This one is a heavily rate-limited development
# key. Quit judging me.
base_url = "https://developer.cumtd.com/api/v2.2/json/{method}?key=f87fa15a173b409aa117f7b5bd539c27"

def get_stop_data(stop):
    payload = {"stop_id": stops[stop.lower().replace("the ","")]}
    r = requests.get(base_url.format(method="GetDeparturesByStop"), params=payload)
    return json.loads(r.text)

def GetStopDepartures(stop):
    data = get_stop_data(stop)['departures']
    out = []
    for departure in data:
        filtered = {q:departure[q] for q in ('headsign','scheduled', 'expected', 'expected_mins') if q in departure}
        filtered['route'] = int(departure['route']['route_short_name'])
        out.append(filtered)
    return out

def GetNamedStopDepartures(bus_num, stop):
    data = GetStopDepartures(stop)
    return [q for q in data if q['route'] == bus_num]
