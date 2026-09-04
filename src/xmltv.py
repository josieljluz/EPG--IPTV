import gzip

from lxml import etree


def format_datetime(value):

    return value.strftime(
        "%Y%m%d%H%M%S %z"
    )


def build_xmltv(
    channels,
    programmes
):

    root = etree.Element(
        "tv",
        attrib={
            "generator-info-name":
                "Python IPTV EPG Generator",
            "generator-info-url":
                "https://github.com"
        }
    )

    for channel in channels:

        channel_element = etree.SubElement(
            root,
            "channel",
            id=channel["id"]
        )

        display_name = etree.SubElement(
            channel_element,
            "display-name",
            lang="pt"
        )

        display_name.text = channel[
            "name"
        ]

    for programme in sorted(
        programmes,
        key=lambda item: item.start
    ):

        programme_element = etree.SubElement(
            root,
            "programme",
            start=format_datetime(
                programme.start
            ),
            stop=format_datetime(
                programme.stop
            ),
            channel=programme.channel_id
        )

        title = etree.SubElement(
            programme_element,
            "title",
            lang="pt"
        )

        title.text = programme.title

        if programme.description:

            description = etree.SubElement(
                programme_element,
                "desc",
                lang="pt"
            )

            description.text = (
                programme.description
            )

        if programme.category:

            category = etree.SubElement(
                programme_element,
                "category",
                lang="pt"
            )

            category.text = programme.category

    return etree.ElementTree(
        root
    )


def save_xml(
    tree,
    path
):

    tree.write(
        path,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )


def save_gzip(
    xml_path,
    gzip_path
):

    with open(
        xml_path,
        "rb"
    ) as source:

        with gzip.open(
            gzip_path,
            "wb"
        ) as target:

            target.writelines(
                source
            )