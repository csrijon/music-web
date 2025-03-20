"""
This is the main file that runs the FastAPI server and serves the API.
"""

import aiohttp
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from wavey import Wavey

load_dotenv()

app = Wavey()
app.mount("/static", StaticFiles(directory="./static/"), name="static")


async def on_startup():
    """
    Create a client session on startup.
    """
    app.client_session = aiohttp.ClientSession()


async def on_shutdown():
    """Close the client session on shutdown."""
    await app.client_session.close()


app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


@app.get("/")
async def root():
    """Serve the index.html file."""
    with open("static/index.html", "rb") as file:
        return HTMLResponse(content=file.read(), status_code=200)


@app.get("/api/search/songs")
async def search_songs(q: str):
    """Search for songs."""
    return await app.query_songs(q)


@app.get("/api/search/related/{song_id}/{language}")
async def search_related(song_id: str, language: str):
    """Search for related songs."""
    return await app.query_related_songs(song_id, language)


@app.get("/api/trending")
async def trending():
    """Fetch the trending songs."""
    return await app.fetch_trending_songs()


@app.get("/api/global")
async def global_songs():
    """Fetch the globally trending songs."""
    return await app.fetch_global_songs()


@app.get("/api/popular")
async def popular():
    """Fetch the most searched songs."""
    return await app.fetch_most_searched()


@app.get("/api/genre")
async def playlist_by_genre(q: str):
    return await app.fetch_songs_by_genre(q)


@app.get("/cdn/thumbnail/{path}")
async def thumbnail(path: str):
    """Stream the thumbnail for a song."""
    stream, length = await app.stream_thumbnail(path)
    headers = {
        "accept-ranges": "bytes",
        "content-type": "image/jpeg",
        "content-length": str(length),
    }
    return StreamingResponse(stream, headers=headers)


@app.get("/cdn/audio/{path}")
async def audio(path: str):
    """Stream the audio for a song."""
    stream, length = await app.stream_audio(path)
    headers = {
        "accept-ranges": "bytes",
        "content-type": "audio/mpeg",
        "content-length": str(length),
    }
    return StreamingResponse(stream, headers=headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
