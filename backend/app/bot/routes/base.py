from pathlib import Path

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineQueryResultArticle
from aiogram.types import InputTextMessageContent
from aiogram.types import WebAppInfo
from aiogram.utils.web_app import check_webapp_signature
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

HTML_PATH = Path(__file__).parent.parent.resolve() / "static/html"


async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    if not check_webapp_signature(bot.token, data["_auth"]):
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    return json_response({"ok": True})


async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=bot.token,
            init_data=data["_auth"],
        )
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    print(data)
    reply_markup = None
    if data["with_webview"] == "1":
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open",
                        web_app=WebAppInfo(url=str(request.url.with_scheme("https"))),
                    ),
                ],
            ],
        )
    await bot.answer_web_app_query(
        web_app_query_id=web_app_init_data.query_id,
        result=InlineQueryResultArticle(
            id=web_app_init_data.query_id,
            title="Demo",
            input_message_content=InputTextMessageContent(
                message_text="Hello, World!",
                parse_mode=None,
            ),
            reply_markup=reply_markup,
        ),
    )
    return json_response({"ok": True})
