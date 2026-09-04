#!/usr/bin/env python3

import json
import logging

from pathlib import Path
from datetime import datetime, timedelta

import pytz

from src.config import (
    load_sources,
    load_channels
)

from src.iptv_org import IPTVOrg

from src.xmltv import (
    build_xmltv,
    save_xml,
    save_gzip
)

from src.sources.guiadetv import (
    GuiaDeTVSource
)

from src.sources.mitv import (
    MiTVSource
)

from src.sources.tvmap import (
    TVMapSource
)

from src.sources.alepi import (
    AlepiSource
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(
    "EPG"
)


ROOT = Path(
    __file__
).resolve().parent

OUTPUT = ROOT / "output"

OUTPUT.mkdir(
    exist_ok=True
)


def create_sources(
    config,
    timezone
):

    sources = []

    source_config = config[
        "sources"
    ]

    if source_config[
        "alepi"
    ].get("enabled"):

        sources.append(
            (
                source_config[
                    "alepi"
                ].get(
                    "priority",
                    0
                ),
                AlepiSource(
                    source_config[
                        "alepi"
                    ],
                    timezone
                )
            )
        )

    if source_config[
        "guiadetv"
    ].get("enabled"):

        sources.append(
            (
                source_config[
                    "guiadetv"
                ].get(
                    "priority",
                    1
                ),
                GuiaDeTVSource(
                    source_config[
                        "guiadetv"
                    ],
                    timezone
                )
            )
        )

    if source_config[
        "mitv"
    ].get("enabled"):

        sources.append(
            (
                source_config[
                    "mitv"
                ].get(
                    "priority",
                    2
                ),
                MiTVSource(
                    source_config[
                        "mitv"
                    ],
                    timezone
                )
            )
        )

    if source_config[
        "tvmap"
    ].get("enabled"):

        sources.append(
            (
                source_config[
                    "tvmap"
                ].get(
                    "priority",
                    3
                ),
                TVMapSource(
                    source_config[
                        "tvmap"
                    ],
                    timezone
                )
            )
        )

    sources.sort(
        key=lambda item: item[0]
    )

    return [
        source
        for _, source in sources
    ]


def remove_duplicates(
    programmes
):

    unique = {}

    for programme in programmes:

        key = programme.key()

        if key not in unique:

            unique[key] = programme

    return list(
        unique.values()
    )


def generate_playlist(
    channels
):

    playlist = [
        "#EXTM3U"
    ]

    for channel in channels:

        playlist.append(
            (
                f'#EXTINF:-1 '
                f'tvg-id="{channel["id"]}" '
                f'tvg-name="{channel["name"]}",'
                f'{channel["name"]}'
            )
        )

        playlist.append(
            ""
        )

    path = OUTPUT / "playlist.m3u"

    path.write_text(
        "\n".join(playlist),
        encoding="utf-8"
    )


def main():

    logger.info(
        "Iniciando geração do EPG"
    )

    config = load_sources()

    channels = load_channels()

    timezone = pytz.timezone(
        config.get(
            "timezone",
            "America/Fortaleza"
        )
    )

    days_ahead = config.get(
        "days_ahead",
        2
    )

    logger.info(
        "Carregando base IPTV-Org"
    )

    aliases = {}

    iptv_config = config[
        "sources"
    ].get(
        "iptv_org"
    )

    if iptv_config and iptv_config.get(
        "enabled"
    ):

        try:

            iptv_org = IPTVOrg(
                iptv_config
            )

            aliases = (
                iptv_org.build_alias_map(
                    channels
                )
            )

            logger.info(
                "Mapeamento IPTV-Org concluído: %s canais",
                len(aliases)
            )

        except Exception as error:

            logger.warning(
                "Erro IPTV-Org: %s",
                error
            )

    with open(
        OUTPUT / "epg_aliases.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            aliases,
            file,
            ensure_ascii=False,
            indent=4
        )

    sources = create_sources(
        config,
        timezone
    )

    programmes = []

    today = datetime.now(
        timezone
    ).date()

    for day_offset in range(
        days_ahead + 1
    ):

        current_date = (
            today
            + timedelta(
                days=day_offset
            )
        )

        logger.info(
            "Processando data %s",
            current_date
        )

        for channel in channels:

            logger.info(
                "Canal: %s",
                channel["name"]
            )

            channel_programmes = []

            for source in sources:

                try:

                    logger.info(
                        "Tentando fonte: %s",
                        source.name
                    )

                    result = source.fetch(
                        channel,
                        current_date
                    )

                    if result:

                        channel_programmes = result

                        logger.info(
                            "Fonte %s retornou %s programas",
                            source.name,
                            len(result)
                        )

                        break

                except Exception as error:

                    logger.warning(
                        "%s falhou para %s: %s",
                        source.name,
                        channel["name"],
                        error
                    )

            programmes.extend(
                channel_programmes
            )

    programmes = remove_duplicates(
        programmes
    )

    logger.info(
        "Total de programas: %s",
        len(programmes)
    )

    tree = build_xmltv(
        channels,
        programmes
    )

    xml_path = (
        OUTPUT / "epg.xml"
    )

    gzip_path = (
        OUTPUT / "epg.xml.gz"
    )

    save_xml(
        tree,
        xml_path
    )

    save_gzip(
        xml_path,
        gzip_path
    )

    generate_playlist(
        channels
    )

    logger.info(
        "EPG gerado com sucesso"
    )

    logger.info(
        "Arquivo XML: %s",
        xml_path
    )

    logger.info(
        "Arquivo GZIP: %s",
        gzip_path
    )


if __name__ == "__main__":

    main()