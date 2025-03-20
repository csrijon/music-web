"""
This module contains the models for the API.
"""

import re
from typing import Dict, Any

from .crypto import encrypt, b64_decrypt


def mask_thumb_url(url: str):
    pattern = r'/(?:\d+|null)/[^/]+(?=-\d+x\d+\.jpg)'
    part = re.search(pattern, url).group().encode()
    return encrypt(part)


def mask_media_signature(sig: str):
    return encrypt(b64_decrypt(sig))


def clean_song_with_more_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean the song data and return a flat dictionary.
    """

    primary_artists = list(data["more_info"]["artistMap"]["primary_artists"])
    artists = ", ".join([a["name"] for a in primary_artists])
    return {
        "title": data["title"],
        "album": data["more_info"]["album"],
        "album_id": data["more_info"]["album_id"],
        "duration": data["more_info"]["duration"],
        "id": data["id"],
        "year": data["year"],
        "singer": artists,
        "language": data["language"],
        "label": data["more_info"]["label"],
        "thumb_signature": mask_thumb_url(data["image"]),  # type: ignore
        "media_signature": mask_media_signature(data["more_info"]["encrypted_media_url"]),
    }


def clean_raw_song_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean the raw song data and return a flat dictionary.
    """
    artists = ", ".join(list(data["artistMap"]))
    return {
        "title": data["song"],
        "album": data["album"],
        "album_id": data["albumid"],
        "duration": data["duration"],
        "id": data["id"],
        "year": data["year"],
        "singer": artists,
        "language": data["language"],
        "label": data["label"],
        "thumb_signature": mask_thumb_url(data["image"]),
        "media_signature": mask_media_signature(data["encrypted_media_url"]),
    }
