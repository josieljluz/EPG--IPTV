from datetime import datetime, timedelta

from playwright.sync_api import (
    sync_playwright
)

from src.models import Programme
from src.sources.base import BaseSource
from src.utils import (
    normalize_text,
    clean_title
)


class MiTVSource(BaseSource):

    name = "mitv"

    def fetch(
        self,
        channel,
        date
    ):

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

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            try:

                page.goto(
                    self.config["url"],
                    timeout=60000,
                    wait_until="networkidle"
                )

                text = page.locator(
                    "body"
                ).inner_text()

                lines = text.splitlines()

                channel_found = False

                current_time = None

                for line in lines:

                    line = line.strip()

                    if not line:
                        continue

                    normalized = normalize_text(
                        line
                    )

                    if any(
                        alias == normalized
                        for alias in aliases
                    ):

                        channel_found = True

                        continue

                    if channel_found:

                        import re

                        match = re.match(
                            r"^(\d{1,2}:\d{2})\s+(.+)$",
                            line
                        )

                        if match:

                            if current_time:

                                start = current_time

                                stop = datetime.combine(
                                    date,
                                    datetime.min.time()
                                )

                                hour, minute = map(
                                    int,
                                    match.group(1).split(":")
                                )

                                stop = stop.replace(
                                    hour=hour,
                                    minute=minute
                                )

                                stop = self.timezone.localize(
                                    stop
                                )

                                programmes[-1].stop = stop

                            hour, minute = map(
                                int,
                                match.group(1).split(":")
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

                            programmes.append(
                                Programme(
                                    channel_id=channel["id"],
                                    title=clean_title(
                                        match.group(2)
                                    ),
                                    start=start,
                                    stop=start + timedelta(
                                        hours=1
                                    ),
                                    source=self.name
                                )
                            )

                            current_time = start

            finally:

                browser.close()

        return programmes