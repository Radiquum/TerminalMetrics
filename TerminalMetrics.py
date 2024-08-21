import os
import requests
import time
from timeloop import Timeloop
from datetime import timedelta
import logging
from dotenv import load_dotenv
load_dotenv()

tl = Timeloop()
logging.getLogger("timeloop").setLevel(logging.CRITICAL)

API_BASE = "https://analytics.wah.su/api/v1/stats"
API_KEY = os.getenv("API_KEY")
SITE_ID = os.getenv("SITE_ID")

STAT_UPDATE_SEC = 30
NEXT_UPDATE_TIME = STAT_UPDATE_SEC

@tl.job(interval=timedelta(seconds=STAT_UPDATE_SEC))
def updateCurrentStatistics():
    realtime = requests.get(f"{API_BASE}/realtime/visitors?site_id={SITE_ID}&key={API_KEY}", headers={"Authorization": f"Bearer {API_KEY}"})
    if realtime.status_code == 200:
        visitors = realtime.json()
        print(f"\033[H\033[3B\033[1000D\033[K\033[32m\033[0m CURRENT{' ':<4}| {visitors:<8} | {' ':<9} |")

    today = requests.get(f"{API_BASE}/aggregate?site_id={SITE_ID}&key={API_KEY}&period=day&metrics=visitors,pageviews", headers={"Authorization": f"Bearer {API_KEY}"})
    if today.status_code == 200:
        data = today.json()
        print(f"\033[H\033[4B\033[1000D\033[K\033[32m\033[0m DAY{' ':<8}| {data['results']['visitors']['value']:<8} | {data['results']['pageviews']['value']:<9} |")

    week = requests.get(f"{API_BASE}/aggregate?site_id={SITE_ID}&key={API_KEY}&period=7d&metrics=visitors,pageviews", headers={"Authorization": f"Bearer {API_KEY}"})
    if week.status_code == 200:
        data = week.json()
        print(f"\033[H\033[5B\033[1000D\033[K\033[32m󰨳\033[0m WEEK{' ':<7}| {data['results']['visitors']['value']:<8} | {data['results']['pageviews']['value']:<9} |")

    month = requests.get(f"{API_BASE}/aggregate?site_id={SITE_ID}&key={API_KEY}&period=month&metrics=visitors,pageviews", headers={"Authorization": f"Bearer {API_KEY}"})
    if month.status_code == 200:
        data = month.json()
        print(f"\033[H\033[6B\033[1000D\033[K\033[32m󰸗\033[0m MONTH{' ':<6}| {data['results']['visitors']['value']:<8} | {data['results']['pageviews']['value']:<9} |")

@tl.job(interval=timedelta(seconds=1))
def updateNextUpdateTime():
    global NEXT_UPDATE_TIME
    NEXT_UPDATE_TIME = NEXT_UPDATE_TIME - 1
    if NEXT_UPDATE_TIME == 0:
        print(f"\033[H\033[7B\033[1000D\033[K\033[0m\033[32m\033[0m Updating . . .")
        NEXT_UPDATE_TIME = STAT_UPDATE_SEC
    else:
        print(f"\033[H\033[7B\033[1000D\033[K\033[0m\033[33m\033[0m Next update in {NEXT_UPDATE_TIME} seconds")

if __name__ == "__main__":
    print("\033[2J")
    time.sleep(0.1)
    print(f"\033[H\033[1m  {SITE_ID} Plausible Metrics \033[0m")
    print(f"\033[H\033[2B\033[1m  PERIOD{' ':<5}| VISITORS | PAGEVIEWS |\033[0m")
    updateCurrentStatistics()
    tl.start(block=True)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            tl.stop()
        break