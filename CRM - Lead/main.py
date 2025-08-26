from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
import sys
import os
from create_lead_api import add_lead_in_crm
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

# Create Flask app
app = Flask(__name__)
swagger = Swagger(app)
app.config['JSON_SORT_KEYS'] = False





def create_lead(contact_number):
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
