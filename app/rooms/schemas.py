from pydantic import BaseModel
from datetime import datetime

class CreateRoomRequest(BaseModel):
    name: set
    description: str =""
    
class RoomResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_by: int
    created_at : datetime
    
    