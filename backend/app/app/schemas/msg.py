from __future__ import annotations

from pydantic import BaseModel


class Msg(BaseModel):
    msg: str
