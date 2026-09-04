import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.models import Programme
from src.sources.base import BaseSource


class AlepiSource(BaseSource):

    name = "alepi"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(EPG IPTV Generator)"
        )
    }

    def fetch(
        self,
        channel,
        date
    ):

        response = requests.get(
            self.config["url"],
            headers=self.HEADERS,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        programmes = []

        text = soup.get_text(
            "\n",
            strip=True
        )

        import re

        matches = re.findall(
            r"(\d{1,2}:\d{2})\s*[-–]\s*(.+)",
            text
        )

        for index, match in enumerate(
            matches
        ):

            try:

                hour, minute = map(
                    int,
                    match[0].split(":")
                )

                start = datetime.combine(
                    date,
                    datetime.min.time()
                )

                start = start.replace(
                    hour=hour,
                    minute=minute
                )

                start = self.timezone.localize(
                    start
                )

                stop = start + timedelta(
                    hours=1
                )

                programmes.append(
                    Programme(
                        channel_id=channel["id"],
                        title=match[1].strip(),
                        start=start,
                        stop=stop,
                        source=self.name
                    )
                )

            except Exception:
                continue

        return programmes