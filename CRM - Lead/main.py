import ast
import json
from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
import sys
import os
from create_lead_api import add_lead_in_crm
from crm_to_db import crm_to_huse
from flasgger import Swagger

# Load API key from environment variables
API_KEY = os.getenv("HUSE_API_KEY")
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

# Define a Pydantic model for CRM data
class CrmRequest(BaseModel):
    message: str = None
    data: dict
    lead_form_url: str = None
    aml_result_url: str = None
    failure: bool = False

class CrmToHuseData(BaseModel):
    name: str
    phone: str
    email: str
    suggested_membership_tier: str
    company: str
    lead_status: str
    preferred_nickname: str = None
    date_of_birth: str = None
    nationality: str = None
    residential_address: str = None
    passport_number: str = None
    id_number: str = None
    occupation: str = None
    job_title: str = None
    linkedin_or_website: str = None
    education_background: str = None
    notable_affiliations: str = None
    lead_comments: str = None
    approval_status: str = None
    crm_backend_id: str = None
    status: str = None

# Create Flask app0       
app = Flask(__name__)
swagger = Swagger(app)
app.config['JSON_SORT_KEYS'] = False




@app.route("/", methods=["GET"])
def read_root():
    """
    Health check endpoint
    ---
    tags:
      - health
    responses:
      200:
        description: API status
        schema:
          type: object
          properties:
            Hello:
              type: string
              example: "World"
            status:
              type: string
              example: "API is running"
    """
    return jsonify({"Hello": "World", "status": "API is running"})

huse_api_key = os.getenv("HUSE_API_KEY")

@app.route("/create_lead/<contact_number>", methods=["POST"])
def create_lead(contact_number):
    """
    Create a new lead in the CRM system
    ---
    tags:
      - leads
    parameters:
      - name: contact_number
        in: path
        type: string
        required: true
        description: The contact number for the sales agent
      - name: huse-api-key
        in: header
        type: string
        required: true
        description: API key for authentication
      - name: body
        in: body
        required: true
        description: Lead information
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                full_legal_name:
                  type: string
                phone_number:
                  type: string
                email_address:
                  type: string
                suggested_membership_tier:
                  type: string
                company:
                  type: string
                lead_status:
                  type: string
              required:
                - full_legal_name
                - phone_number
                - email_address
                - suggested_membership_tier
                - company
                - lead_status
          required:
            - data
    responses:
      200:
        description: Lead created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            huse_response:
              type: object
            contact_number:
              type: string
            lead_data:
              type: object
      400:
        description: Bad request - validation error or missing data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Validation failed"
            details:
              type: array
              items:
                type: object
      401:
        description: Unauthorized - invalid or missing API key
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unauthorized"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Internal server error: ..."
    """
    try:
        # Check API key authentication
        api_key = request.headers.get("huse-api-key")
        print("Api key from headers, ", api_key)
        print("Api key from env", API_KEY)
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
            
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate using Pydantic models
        try:
            # Try to parse as LeadRequest (with data wrapper) first
            if 'data' in json_data:
                lead_request = LeadRequest(**json_data)
                lead_data = lead_request.data
            else:
                # If no data wrapper, parse directly as LeadData
                lead_data = LeadData(**json_data)
                
        except ValidationError as e:
            return jsonify({
                "error": "Validation failed",
                "details": e.errors()
            }), 400
            
        print(f"Contact number: {contact_number}, Lead data: {lead_data}")
        
        # Validate contact number
        if not contact_number or not contact_number.strip():
            return jsonify({"error": "Contact number is required"}), 400
        
        # Call add_lead with all required parameters
        response = add_lead_in_crm(
            contact_number=contact_number,  # Sales agent's contact (from path)
            full_name=lead_data.full_legal_name,
            phone_number=lead_data.phone_number,  # Lead's phone number
            email_address=lead_data.email_address,
            suggested_membership_tier=lead_data.suggested_membership_tier,
            company=lead_data.company,
            lead_status=lead_data.lead_status
        )
        
        # Check if the response indicates failure
        if isinstance(response, dict) and response.get("failure"):
            return jsonify({
                "error": response.get("error", "Failed to create lead")
            }), 400
        
        return jsonify({
            "message": f"Successfully created lead for contact number: {contact_number}",
            "huse_response": response,
            "contact_number": contact_number,
            "lead_data": {
                "full_name": lead_data.full_legal_name,
                "phone_number": lead_data.phone_number,
                "email_address": lead_data.email_address,
                "suggested_membership_tier": lead_data.suggested_membership_tier,
                "company": lead_data.company,
                "lead_status": lead_data.lead_status,
                "crm_response": response
            }
        })
        
    except Exception as e:
        print(f"Error in create_lead: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/crm_to_huse", methods=["POST"])
def crm_to_huse_api():
    try:
        # Check API key authentication
        api_key = request.headers.get("huse-api-key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
            
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate using Pydantic model
        try:
            lead_data = CrmToHuseData(**json_data)
        except ValidationError as e:
            return jsonify({
                "error": "Validation failed",
                "details": e.errors()
            }), 400
            
        print(f"Adding lead to Huse database: {lead_data.name}")
        
        # Call crm_to_huse function with all parameters
        huse_response = crm_to_huse(
            name=lead_data.name,
            phone=lead_data.phone,
            email=lead_data.email,
            suggested_membership_tier=lead_data.suggested_membership_tier,
            company=lead_data.company,
            lead_status=lead_data.lead_status,
            preferred_nickname=lead_data.preferred_nickname,
            date_of_birth=lead_data.date_of_birth,
            nationality=lead_data.nationality,
            residential_address=lead_data.residential_address,
            passport_number=lead_data.passport_number,
            id_number=lead_data.id_number,
            occupation=lead_data.occupation,
            job_title=lead_data.job_title,
            linkedin_or_website=lead_data.linkedin_or_website,
            education_background=lead_data.education_background,
            notable_affiliations=lead_data.notable_affiliations,
            lead_comments=lead_data.lead_comments,
            approval_status=lead_data.approval_status,
            crm_backend_id=lead_data.crm_backend_id,
            status=lead_data.status
        )
        
        # Check if the response indicates failure
        if isinstance(huse_response, dict) and huse_response.get("failure"):
            return jsonify({
                "error": huse_response.get("error", "Failed to add lead to Huse database")
            }), 400
        
        return jsonify({
            "message": "Successfully added lead to Huse database",
            "huse_response": huse_response
        })
        
    except Exception as e:
        print(f"Error in crm_to_huse_api: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
