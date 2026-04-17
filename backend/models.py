from pydantic import BaseModel

class PlayerRequest(BaseModel):
    summoner: str
    tag:      str
    region:   str = "asia"