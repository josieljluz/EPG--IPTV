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


class TVMapSource(BaseSource):

    name = "tvmap"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0"
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

        aliases = [
            normalize_text(channel["name"])
        ]

        aliases.extend(
            normalize_text(alias)
            for alias in channel.get(
                "aliases",
                []
            )
        )

        for element in soup.find_all(
            ["div", "article", "section"]
        ):

            text = element.get_text(
                " ",
                strip=True
            )

            normalized = normalize_text(
                text
            )

            if not any(
                alias in normalized
                for alias in aliases
            ):
                continue

            matches = re.findall(
                r"(\d{1,2}:\d{2})\s+(.+?)(?=\d{1,2}:\d{2}|$)",
                text
            )

            for index, match in enumerate(
                matches
            ):

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
                        title=clean_title(
                            match[1]
                        ),
                        start=start,
                        stop=stop,
                        source=self.name
                    )
                )

        return programmes