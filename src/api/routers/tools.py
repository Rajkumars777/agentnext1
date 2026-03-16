from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import os
from typing import List, Optional

router = APIRouter(prefix="/tools", tags=["tools"])

class BrowseRequest(BaseModel):
    url: str

@router.get("/files")
async def list_files(directory: str = Query(".", description="Directory to list")):
    """List files in the specified directory."""
    try:
        # Resolve path relative to project root or absolute
        abs_path = os.path.abspath(directory)
        
        # Security check: Limit to current drive/user home for sanity (basic)
        # In a real app, this should be more restricted
        
        items = []
        if os.path.isdir(abs_path):
            for entry in os.scandir(abs_path):
                items.append({
                    "name": entry.name,
                    "isDir": entry.is_dir(),
                    "size": entry.stat().st_size if entry.is_file() else None,
                })
            return {"directory": abs_path, "items": items}
        else:
            raise HTTPException(status_code=404, detail="Directory not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/browser/browse")
async def browse_url(req: BrowseRequest):
    """Placeholder for browser control."""
    return {
        "success": True, 
        "message": f"Browser request for {req.url} received."
    }

# --- Desktop Management ---

class DesktopAppRequest(BaseModel):
    app_name: str

@router.get("/desktop/processes")
async def list_processes():
    from src.capabilities.desktop import list_processes as lp
    return {"processes": lp()}

@router.post("/desktop/open")
async def open_desktop_app(req: DesktopAppRequest):
    from src.capabilities.desktop import open_app
    return open_app(req.app_name)

@router.post("/desktop/close")
async def close_desktop_app(req: DesktopAppRequest):
    from src.capabilities.desktop import close_app
    return close_app(req.app_name)
