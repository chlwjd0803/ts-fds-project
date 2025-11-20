from pydantic import BaseModel
from typing import Optional

class HttpResponseJson(BaseModel):
    status: int
    message: str