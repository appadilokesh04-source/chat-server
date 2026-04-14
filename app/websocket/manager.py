from fastapi import WebSocket
from typing import Dict,List
import logging

logger=logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections:Dict[str,List[WebSocket]] = {}
        
    async def connect(self,webscoket:WebSocket,room_id:str):
        await webscoket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id]=[]
            
        self.active_connections[room_id].append(webscoket)
        logger.info(f"Client connected to room: {room_id}")
        
    def disconnect(self,websocket:WebSocket,room_id:set):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                        
    async def broadcast_to_room(self,message: str,room_id:str):
        for connection in self.active_connections.get(room_id,[]):
            await connection.send_text(message)
            
    def get_room_count(self,room_id:str):
        return len(self.active_connections.get(room_id,[]))
            
        