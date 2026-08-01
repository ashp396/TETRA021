"""Broadcasts discrepancy comments, task updates, and document changes to
everyone currently viewing the same workspace, so collaboration feels live
without anyone needing to refresh."""
from fastapi import WebSocket

class WorkspaceHub:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, workspace_id: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(workspace_id, []).append(ws)

    def disconnect(self, workspace_id: str, ws: WebSocket):
        if workspace_id in self.rooms and ws in self.rooms[workspace_id]:
            self.rooms[workspace_id].remove(ws)

    async def broadcast(self, workspace_id: str, message: dict):
        for ws in list(self.rooms.get(workspace_id, [])):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(workspace_id, ws)

hub = WorkspaceHub()
