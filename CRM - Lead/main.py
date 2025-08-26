from typing import Union, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from create_lead_api import add_lead_in_crm

# Define a Pydantic model for the lead data
class LeadData(BaseModel):
    full_legal_name: str
    phone_number: str
    email_address: str
    suggested_membership_tier: str
    company: str
    lead_status: str

# Define a Pydantic model for the request body with data wrapper
class LeadRequest(BaseModel):
    data: LeadData

# Create FastAPI app with metadata for better Swagger docs
app = FastAPI(
    title="CRM Lead Management API",
    description="A simple API for managing CRM leads. ",
    version="1.0.0",
)

# Tags metadata for better organization in Swagger docs
tags_metadata = [
    {
        "name": "health",
        "description": "Health check endpoints",
    },
    {
        "name": "leads",
        "description": "Lead management operations. Create and manage CRM leads.",
    },
]


@app.get("/", tags=["health"])
def read_root():
    """
    Health check endpoint.
    
    Returns a simple greeting to verify the API is running.
    """
    return {"Hello": "World", "status": "API is running"}


@app.post("/create_lead/{contact_number}", tags=["leads"])
async def create_lead(contact_number: str, lead_data: LeadRequest):
    """
    Create a new lead in the CRM system.
    
    - **contact_number**: The contact number for the sales agent (required)
    - **lead_data**: Lead information including full name, phone, email, etc. (required)
    
    Returns a success message if the lead is created successfully.
    
    """
    print(f"Contact number: {contact_number}, Lead data: {lead_data}")
    try:
        # Validate contact number
        if not contact_number or not contact_number.strip():
            raise HTTPException(
                status_code=400,
                detail="Contact number is required"
            )
        
        # Call add_lead with all required parameters
        response = add_lead_in_crm(
            contact_number=contact_number,  # Sales agent's contact (from path)
            full_name=lead_data.data.full_legal_name,
            phone_number=lead_data.data.phone_number,  # Lead's phone number
            email_address=lead_data.data.email_address,
            suggested_membership_tier=lead_data.data.suggested_membership_tier,
            company=lead_data.data.company,
            lead_status=lead_data.data.lead_status
        )
        
        # Check if the response indicates failure
        if isinstance(response, dict) and response.get("failure"):
            raise HTTPException(
                status_code=400,
                detail=response.get("error", "Failed to create lead")
            )
        
        return {
            "message": f"Successfully created lead for contact number: {contact_number}",
            "huse_response": response,
            "contact_number": contact_number,
            "lead_data": {
                "full_name": lead_data.data.full_legal_name,
                "phone_number": lead_data.data.phone_number,
                "email_address": lead_data.data.email_address,
                "suggested_membership_tier": lead_data.data.suggested_membership_tier,
                "company": lead_data.data.company,
                "lead_status": lead_data.data.lead_status,
                "crm_response": response
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

