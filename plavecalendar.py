import requests
from datetime import datetime
from ics import Calendar, Event
import pytz
import time
import os
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

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
    try:
        utc_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        utc_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    # utc_dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")
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

# #生成ics文件
# def write_ics(calendar,filename = "plavecalendar.ics"):
#     with open(filename, "w", encoding="utf-8") as f:
#         f.writelines(calendar)
#         print("ICS 文件生成成功")


def generate_calendar(yearmonth):
    new_calendar = Calendar()
    seen = set()
    for year, month in yearmonth:
        print("Fetching", year, month)
        events = get_calendar_events(month, year)
        for item in events:
            uid = item["id"]
            if uid in seen:
                continue
            seen.add(uid)
            event = build_event(item)
            new_calendar.events.add(event)
        time.sleep(1)  # 防止请求太快
    return new_calendar

def read_ics(filename_ics="plavecalendar.ics"):
    if os.path.exists(filename_ics):
        with open(filename_ics, "r", encoding="utf-8") as f:
            calendar = Calendar(f.read())
            old_events = {event.uid: event for event in calendar.events}
        return old_events,calendar
    else:
        print("无ics历史文件")

def datefrom30to120():
    local_tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(local_tz)

    window_start = now - timedelta(days=30)
    window_end = now + timedelta(days=120)

    return window_start, window_end

def rangeyearmonth():
    now = datetime.now(timezone.utc)
    months_to_sync = []
    for i in range(-1, 4):
        target = now + relativedelta(months=i)
        months_to_sync.append((target.year, target.month))
    return months_to_sync

def sycsync_calendar(old_calendar, old_events, new_calendar):
    # 新数据字典
    new_events = {event.uid: event for event in new_calendar.events}

    # 旧数据字典
    old_dict = old_events

    # UID 集合
    new_uids = set(new_events.keys())
    old_uids = set(old_dict.keys())

    # 🔹 1️⃣ 新增
    for uid in new_uids - old_uids:
        old_calendar.events.add(new_events[uid])

    # 🔹 2️⃣ 更新
    for uid in new_uids & old_uids:
        new_event = new_events[uid]
        old_event = old_dict[uid]

        if (
                old_event.name != new_event.name
                or old_event.begin != new_event.begin
                or old_event.description != new_event.description
        ):
            old_calendar.events.remove(old_event)
            old_calendar.events.add(new_event)

    # 🔹 3️⃣ 删除（只删窗口内）
    start, end = datefrom30to120()

    for uid in old_uids - new_uids:
        old_event = old_dict[uid]

        if start <= old_event.begin <= end:
            old_calendar.events.remove(old_event)

    return old_calendar


def write_ics(calendar, filename="plavecalendar.ics"):
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(calendar)
    print("ICS 文件生成成功")

def main():
    old_events,old_calendar = read_ics("plavecalendar.ics")
    date = rangeyearmonth()
    new_calendar  = generate_calendar(date)
    calendar = sycsync_calendar(old_calendar,old_events,new_calendar)
    write_ics(calendar, filename="plavecalendar.ics")
    print("完成 ✔")


if __name__ == "__main__":
    main()



