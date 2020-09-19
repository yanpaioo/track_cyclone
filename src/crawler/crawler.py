import re
from datetime import datetime
from time import sleep

import schedule
import urllib3
from bs4 import BeautifulSoup

from src.db.db import PostgreSQLEngine
from src.util.config import Configs

URL = "https://rammb-data.cira.colostate.edu/tc_realtime"
SLEEP_TIME_IN_SEC = 10
EVERY_NTH_HOUR = 1

DB_CONFIG = Configs["db"]
ENGINE = PostgreSQLEngine(
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    db=DB_CONFIG["db"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    echo=DB_CONFIG["echo"])


def make_soup(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data, "html5lib")


def crawl():
    soup = make_soup(URL)

    basin_storms = soup.find_all("div", {"class": "basin_storms"})
    for basin_storm in basin_storms:
        # Get and insert ocean
        ocean = basin_storm.find("h3").get_text()
        ENGINE.insert_ocean(ocean)

        # Get cyclones
        cyclone_info = basin_storm.find_all("a", href=True)
        for info in cyclone_info:
            cyclone_name = info.get_text().strip()

            # Insert cyclone
            ENGINE.insert_cyclone(name=cyclone_name)

            # Crawl info link
            cyclone_url = f"{URL}/{info['href']}"
            cyclone_soup = make_soup(cyclone_url)

            # Get datetime
            current_info = cyclone_soup.find(
                "h4",
                text=re.compile('^Time of Latest Forecast'))

            if current_info:
                datetime_string = current_info.get_text().split(": ")[-1]
                datetime_obj = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')

                # Get cyclone info
                info = cyclone_soup.find_all("tr")[1].find_all("td")
                latitude = float(info[1].get_text())
                longitude = float(info[2].get_text())
                intensity = int(info[3].get_text())

                ENGINE.insert_cyclone_activity(
                    cyclone=cyclone_name,
                    datetime=datetime_obj,
                    ocean=ocean,
                    latitude=latitude,
                    longitude=longitude,
                    intensity=intensity)

    print("Crawling ocean info ...")


def main():
    print("Crawler started ...")
    # schedule.every(EVERY_NTH_HOUR).hour.do(crawl)
    schedule.every(EVERY_NTH_HOUR).second.do(crawl)
    while True:
        schedule.run_pending()
        sleep(SLEEP_TIME_IN_SEC)


if __name__ == "__main__":
    main()
