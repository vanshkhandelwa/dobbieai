import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Doctor Appointment Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add basic routes for testing
@app.get("/")
async def root():
    return {"message": "API is working!"}

@app.get("/api/v1/doctors")
async def get_doctors():
    # Mock data for testing
    return [
        {"id": 1, "full_name": "Dr. Vikram Ahuja", "specialization": "Cardiologist"},
        {"id": 2, "full_name": "Dr. Priya Sharma", "specialization": "Dermatologist"},
        {"id": 3, "full_name": "Dr. Raj Patel", "specialization": "General Physician"}
    ]


@app.post("/api/v1/auth/token")
async def login():
    # Mock authentication for testing with doctor role
    return {
        "access_token": "mock_token_for_testing",
        "token_type": "bearer",
        "user_id": 2,
        "email": "dr.test@example.com",
        "full_name": "Dr. Test Doctor",
        "role": "doctor"  # Changed to doctor role
    }
# Run the application
if __name__ == "__main__":
    uvicorn.run("run_local:app", host="0.0.0.0", port=8000, reload=True)