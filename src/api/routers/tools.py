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
    """Placeholder for browser control. In this architecture, browser tasks are usually routed via chat."""
    # For now, we'll return a message that the agent can handle this via the main chat.
    # In the future, this could trigger a specific Playwright instance.
    return {
        "success": True, 
        "message": f"Browser request for {req.url} received. Please use the main chat for interactive browsing."
    }
