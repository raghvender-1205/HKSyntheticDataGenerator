import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Synthetic Data Generator",
    description="A configurable API for generating LLM datasets for various use cases",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Synthetic Data Generator API"}

# Import routes after app initialization
from api.routes import dataset_routes, datasource_routes, llm_routes, utility_routes

# Include routers with API v1 prefix
app.include_router(dataset_routes.router, prefix="/api/v1")
app.include_router(datasource_routes.router, prefix="/api/v1")
app.include_router(llm_routes.router, prefix="/api/v1")
app.include_router(utility_routes.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 