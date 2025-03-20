"""
This module contains the client for the Wavey service. 
It is responsible for making requests to the Wavey API and
returning the data in a clean format for the API to use.
"""

import asyncio
import json
from typing import Any, List, Tuple, Dict

import aiohttp
from fastapi import FastAPI

from .crypto import decrypt
from .models import clean_raw_song_data, clean_song_with_more_info


class Wavey(FastAPI):
    """
    Contains the API for the Wavey service.
    """

    HOST_URL = "https://www.jiosaavn.com"

    BASIC_HEADERS = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    def __init__(self):
        self.client_session: aiohttp.ClientSession = None  # type: ignore
        super().__init__()

    @staticmethod
    async def _josnify(response: aiohttp.ClientResponse) -> Any:
        return json.loads(await response.read())

    async def request(
            self, method: str = "GET", *, path: str
    ) -> aiohttp.ClientResponse:
        """Make a request to the Wavey API."""
        return await self.client_session.request(
            method, f"{self.HOST_URL}{path}", headers=self.BASIC_HEADERS
        )

    async def query_songs(self, query: str) -> List[Any]:
        """Query the Wavey API for songs."""
        resp = await self.request(
            path=f"/api.php?_format=json&_marker=0&ctx=web6dot0&__call=search.getResults"
                 f"&q={query}&n=1000&pn=1&sort=rel"
        )
        data = await self._josnify(resp)
        data = data["results"]
        return [clean_raw_song_data(song) for song in data]

    async def query_related_songs(self, song_id: str, language: str) -> List[Any]:
        """Query the Wavey API for related songs to a given song."""
        resp = await self.request(
            path=f"/api.php?_format=json&_marker=0&ctx=web6dot0&__call=reco.getreco"
                 f"&api_version=4&pid={song_id}&language={language}"
        )
        data = await self._josnify(resp)
        return [clean_song_with_more_info(song) for song in data]

    async def resolve_song_by_album_perma(self, perma_url: str) -> Dict[str, Any]:
        """Resolve a song by its album perma url."""
        resp = await self.request(
            path=f"/api.php?_format=json&_marker=0&ctx=web6dot0&__call=webapi.get&type=album"
                 f"&link={perma_url}&token={perma_url.split('/')[-1]}"
        )
        return await self._josnify(resp)

    async def resolve_songs_by_album_id(self, album_id: str) -> Dict[str, Any]:
        """Resolve songs by their album id."""
        resp = await self.request(
            path=f"/api.php?_format=json&_marker=0&ctx=web6dot0&__call=content.getAlbumDetails"
                 f"&albumid={album_id}"
        )
        return await self._josnify(resp)

    async def fetch_trending_songs(self) -> Dict[str, Any]:
        """Fetch the trending songs from the Wavey API."""
        resp = await self.request(
            path="/api.php?_format=json&_marker=0&ctx=web6dot0&__call=content.getTrending"
                 "&includeMetaTags=1"
        )
        return await self._josnify(resp)

    async def fetch_global_songs(self) -> List[Any]:
        """Fetch the globally trending songs from the Wavey API."""
        resp = await self.request(
            path="/api.php?_format=json&_marker=0&ctx=web6dot0&__call=webapi.get&token=DjLfyo0wfbk_"
                 "&type=playlist&p=1&n=100&includeMetaTags=0"
        )
        data = await self._josnify(resp)
        songs = data["songs"]
        return [clean_raw_song_data(song) for song in songs]

    async def fetch_most_searched(self) -> Dict[str, Any]:
        """Fetch the most searched songs from the Wavey API."""
        resp = await self.request(
            path="/api.php?_format=json&_marker=0&ctx=web6dot0&__call=search.getTopSearches"
        )
        return await self._josnify(resp)

    async def fetch_songs_by_genre(self, genre: str):
        resp = await self.request(
            path=f"/api.php?p=1&q=playlist+{genre}&_format=json&_marker=0"
                 f"&api_version=4&ctx=web6dot0&n=20&__call=search.getResults"
        )
        pids = await self.extract_playlist_ids(await self._josnify(resp))
        batches = await asyncio.gather(*[self.resolve_songs_by_playlist(pid) for pid in pids])
        raw_songs = []
        for batch in batches:
            raw_songs.extend(batch["list"])
        return [clean_song_with_more_info(song) for song in raw_songs]

    async def resolve_songs_by_playlist(self, pid: str):
        resp = await self.request(
            path=f"/api.php?__call=webapi.get&token={pid}"
                 f"&type=playlist&p=1&n=50&includeMetaTags=0"
                 f"&ctx=web6dot0&api_version=4&_format=json&_marker=0"
        )
        return await self._josnify(resp)

    @staticmethod
    async def extract_playlist_ids(data: Dict[str, Any]) -> List[Any]:
        perma_urls = [data["perma_url"] for data in data["results"]]
        return [perma.split("/")[-1] for perma in perma_urls]

    async def stream_thumbnail(self, path: str) -> Tuple[aiohttp.StreamReader, int]:
        """Stream the thumbnail for a song."""
        signature = decrypt(bytes.fromhex(path))
        if not signature:
            with open("/app/static/placeholder.jpg", "rb") as file:
                data = file.read()
                return data, len(data)  # type: ignore
        resp = await self.client_session.get(f"https://c.saavncdn.com{signature}-500x500.jpg")
        return resp.content, int(resp.headers["content-length"])

    async def stream_audio(self, path: str) -> Tuple[aiohttp.StreamReader, int]:
        """Stream the audio for a song."""
        url = decrypt(bytes.fromhex(path.split("_")[0]))
        url = url.replace("http://", "https://", 1)
        url = url.split("_")[0]
        resp = await self.client_session.get(f"{url}_320.mp4")
        return resp.content, int(resp.headers["content-length"])
