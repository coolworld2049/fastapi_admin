from __future__ import annotations

from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from bot.routes.base import HTML_PATH


async def demo_handler(request: Request):  # noqa
    return FileResponse(HTML_PATH / 'demo.html')
