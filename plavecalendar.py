import requests
from datetime import datetime
from ics import Calendar, Event
import pytz

now = datetime.now()
year = now.year
month = now.month
url = "https://plavecalendar.com/api/events"   # 换成你的接口
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
    "Referer": "https://plavecalendar.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}
params = {
    "year": year,
    "month": month
}
resp = requests.get(url, params=params,headers=headers)
resp.raise_for_status()
if resp.status_code == 200:
    data = resp.json()
    print(data)
    events_data = data["data"] if "data" in data else data
    calendar = Calendar()
    filename = "plavecalendar"+".ics"
    for item in events_data:
        e = Event()
        date = item["utcStart"]
        links = item.get("links",[])
        url = links[0]["url"] if links else None

        utc_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
        cst = pytz.timezone("Asia/Shanghai")
        cst_dt = utc_dt.astimezone(cst)

        if item.get("isAllDay") is True:
            utc_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")
            event_date = utc_dt.date()  # 用UTC日期

            e.begin = event_date
            e.make_all_day()
        else:
            e.begin = cst_dt


        e.name = item["title"]
        e.description = url
        e.uid  = item["id"]

        calendar.events.add(e)
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    print("ICS 文件生成成功")

else:
    print("请求失败:", resp.status_code)




