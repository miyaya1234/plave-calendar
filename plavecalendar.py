import requests
from datetime import datetime
from ics import Calendar, Event
import pytz
import time

def get_calendar_events(month, year):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://plavecalendar.com/",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    session = requests.Session()
    params = {
        "year": year,
        "month": month
    }
    # clouldwork
    resp = session.get(
        "https://blue-firefly-19a3.doubtmyself030.workers.dev/",
        params=params,
        headers=headers,
        timeout=10
    )
    # url = "https://plavecalendar.com/api/events"
    resp.raise_for_status()

    if resp.status_code == 200:
        data = resp.json()
        # print(data)
        events_data = data["data"] if "data" in data else data
        return events_data
    else:
        print("请求失败:", resp.status_code)

#处理拉取数据
def build_event(item):
    e = Event()

    date = item["utcStart"]

    utc_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")
    utc_dt = utc_dt.replace(tzinfo=pytz.UTC)

    local_tz = pytz.timezone("Asia/Shanghai")
    local_dt = utc_dt.astimezone(local_tz)

    if item.get("isAllDay"):
        e.begin = utc_dt.date()
        e.make_all_day()
    else:
        e.begin = local_dt

    links = item.get("links", [])
    url = links[0]["url"] if links else ""

    e.name = item["title"]
    e.description = url
    e.uid = item["id"]

    return e


def write_ics(calendar,filename = "plavecalendar.ics"):
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(calendar)
        print("ICS 文件生成成功")


def generate_calendar(year):
    """抓取全年数据"""
    calendar = Calendar()
    seen = set()
    for m in range(1, 13):
        print("Fetching", year, m)
        events = get_calendar_events(m, year)
        for item in events:
            uid = item["id"]
            if uid in seen:
                continue
            seen.add(uid)
            event = build_event(item)
            calendar.events.add(event)
        time.sleep(1)  # 防止请求太快
    return calendar

#自动抓取当年一年的日程
def main():
    now = datetime.now()
    year = now.year
    calendar = generate_calendar(year)
    write_ics(calendar)
    print("完成 ✔")


if __name__ == "__main__":
    main()



