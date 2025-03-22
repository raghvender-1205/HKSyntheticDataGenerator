from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
import os
from typing import List, Dict, Any
from pathlib import Path
import shutil

router = APIRouter(
    prefix="/utils",
    tags=["utilities"],
    responses={404: {"description": "Not found"}},
)

@router.get("/files", response_model=Dict[str, List[str]])
async def get_files(directory: str = Query("", description="Directory to list files from")):
    """
    Get list of files in the specified directory.
    If no directory is provided, list files in the current directory.
    """
    try:
        # Sanitize and resolve the directory path
        if not directory:
            # Default to the data directory
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            directory = base_dir
        else:
            # Ensure the path is within the allowed directories
            directory = os.path.abspath(directory)
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            if not directory.startswith(base_dir):
                directory = base_dir
        
        # List all files and directories
        items = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                # Include files with their full path
                items.append(str(item_path))
            elif os.path.isdir(item_path):
                # Mark directories with a trailing slash
                items.append(f"{item_path}/")
        
        return {"files": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.get("/file-types", response_model=Dict[str, List[str]])
async def get_file_types():
    """
    Get list of supported file types.
    """
    return {
        "types": ["txt", "json", "csv"]
    }

@router.get("/encodings", response_model=Dict[str, List[str]])
async def get_encodings():
    """
    Get list of supported file encodings.
    """
    return {
        "encodings": ["utf-8", "utf-16", "ascii", "latin-1"]
    }

@router.post("/upload", response_model=Dict[str, str])
async def upload_file(
    file: UploadFile = File(...),
    directory: str = Form(""),
):
    """
    Upload a file to the specified directory.
    If no directory is provided, the file will be saved in the root data directory.
    """
    try:
        # Sanitize and resolve the directory path
        if not directory:
            # Default to the data directory
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            directory = base_dir
        else:
            # Ensure the path is within the allowed directories
            directory = os.path.abspath(directory)
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
            if not directory.startswith(base_dir):
                directory = base_dir
            
            # Create directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Save the file
        file_path = os.path.join(directory, file.filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "filename": file.filename,
            "path": file_path,
            "message": f"File '{file.filename}' uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}") 