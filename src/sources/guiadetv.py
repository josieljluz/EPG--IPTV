import re

import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.models import Programme
from src.sources.base import BaseSource
from src.utils import (
    normalize_text,
    clean_title
)


class GuiaDeTVSource(BaseSource):

    name = "guiadetv"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36"
        )
    }

    def fetch(
        self,
        channel,
        date
    ):

        url = self.config["url"]

        response = requests.get(
            url,
            headers=self.HEADERS,
            timeout=30
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        programmes = []

        channel_names = [
            normalize_text(channel["name"])
        ]

        for alias in channel.get(
            "aliases",
            []
        ):

            channel_names.append(
                normalize_text(alias)
            )

        elements = soup.find_all(
            ["div", "section", "article"]
        )

        for element in elements:

            text = element.get_text(
                " ",
                strip=True
            )

            normalized = normalize_text(text)

            if not any(
                name in normalized
                for name in channel_names
            ):
                continue

            matches = re.findall(
                r"(\d{1,2}:\d{2})\s*[-–]\s*([^0-9]+?)(?=\d{1,2}:\d{2}|$)",
                text
            )

            for index, match in enumerate(matches):

                time_text = match[0]
                title = clean_title(
                    match[1]
                )

                try:

                    hour, minute = map(
                        int,
                        time_text.split(":")
                    )

                    start = datetime.combine(
                        date,
                        datetime.min.time()
                    )

                    start = start.replace(
                        hour=hour,
                        minute=minute
                    )

                    if index + 1 < len(matches):

                        next_time = matches[
                            index + 1
                        ][0]

                        next_hour, next_minute = map(
                            int,
                            next_time.split(":")
                        )

                        stop = datetime.combine(
                            date,
                            datetime.min.time()
                        )

                        stop = stop.replace(
                            hour=next_hour,
                            minute=next_minute
                        )

                    else:

                        stop = start + timedelta(
                            hours=1
                        )

                    programmes.append(
                        Programme(
                            channel_id=channel["id"],
                            title=title,
                            start=self.timezone.localize(
                                start
                            ),
                            stop=self.timezone.localize(
                                stop
                            ),
                            source=self.name
                        )
                    )

                except Exception:
                    continue

        return programmes