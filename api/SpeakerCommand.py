from pydantic import BaseModel
from typing import Optional

class SpeakerCommand(BaseModel):
    deviceId: str
    command: str
    speakerStatus: bool
    duration: int
    message: Optional[str] = None