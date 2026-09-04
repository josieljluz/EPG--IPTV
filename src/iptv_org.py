import requests

from rapidfuzz import process

from src.utils import normalize_text


class IPTVOrg:

    def __init__(
        self,
        config
    ):

        self.channels_url = config[
            "channels_url"
        ]

        self.guides_url = config[
            "guides_url"
        ]

        self.channels = []

    def load_channels(self):

        response = requests.get(
            self.channels_url,
            timeout=60
        )

        response.raise_for_status()

        self.channels = response.json()

        return self.channels

    def find_channel(
        self,
        name,
        country="BR"
    ):

        if not self.channels:
            self.load_channels()

        candidates = []

        for channel in self.channels:

            if (
                country
                and channel.get("country") != country
            ):
                continue

            candidates.append(
                (
                    channel,
                    normalize_text(
                        channel.get("name", "")
                    )
                )
            )

        names = [
            item[1]
            for item in candidates
        ]

        result = process.extractOne(
            normalize_text(name),
            names
        )

        if not result:
            return None

        matched_name = result[0]

        score = result[1]

        if score < 75:
            return None

        for channel, normalized in candidates:

            if normalized == matched_name:
                return channel

        return None

    def build_alias_map(
        self,
        local_channels
    ):

        aliases = {}

        for local in local_channels:

            found = self.find_channel(
                local["name"]
            )

            if found:

                aliases[local["id"]] = {
                    "iptv_org_id": found["id"],
                    "name": found["name"],
                    "country": found.get(
                        "country"
                    )
                }

        return aliases