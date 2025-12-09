import json
import os
import requests
import base64
import hmac
import hashlib
import time
from proxies.lead_proxy import LeadProxy
from datetime import datetime
from CrmMethods.crm_dictionary import build_crm_payload
from dotenv import load_dotenv
load_dotenv()

def crm_create_lead(lead_id: int, crm_token: str):
    # Get the lead details from the draft id
    lead_details = LeadProxy.to_get_complete_by_id(complete_id=int(lead_id))
    print("Lead details:", lead_details)
    employee_name = LeadProxy.get_employee_name_by_crm_token(crm_token=crm_token)
    print("Employee name:", employee_name)
    # Check if lead_details is None
    if lead_details is None:
        print(f"Error: No lead found with ID {lead_id} or database connection issue")
        return {"success": False, "detail": f"No lead found with ID {lead_id}"}

    URL = "https://guest-app-api.therufescent.com/api/leads/crm/create_lead"

    # Base64 client key for HMAC signature
    BASE64_KEY = os.getenv('BASE64_KEY')
    CLIENT_KEY = base64.b64decode(BASE64_KEY).decode('utf-8')

    if lead_details is not None:
        # Parse the full name into first and last name
        crm_data = build_crm_payload(lead_details, employee_name)
        
        # Print the JSON data that will be sent
        print("CRM Data JSON:", json.dumps(crm_data, indent=2))

        try:
            # Include an empty 'documents' field as per the working example
            payload = {"data": crm_data,
                        "documents": {
                            "additionalProp1": "string",
                            "additionalProp2": "string",
                            "additionalProp3": "string"
                        }
                        }
            
            # Generate timestamp and HMAC signature
            timestamp = int(time.time())
            # Serialize payload to exact JSON string (no extra spaces)
            body_string = json.dumps(payload, separators=(',', ':'))
            # For POST requests, message format is: timestamp:body (client key NOT in message, only used as secret)
            message = f"{timestamp}:{body_string}"
            
            # Generate HMAC-SHA256 signature using base64 encoding (as per second example in docs)
            signature_bytes = hmac.new(
                CLIENT_KEY.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
            signature = base64.b64encode(signature_bytes).decode('utf-8')
            
            # Debug prints
            print(f"Timestamp: {timestamp}")
            print(f"Body string length: {len(body_string)}")
            print(f"Message preview: {message[:150]}...")
            print(f"Signature: {signature}")
            
            headers = {
                "Content-Type": "application/json",
                "X-Timestamp": str(timestamp),
                "X-Signature": signature,
                "Authorization": f"Basic{crm_token}",
                "espo-authorization": crm_token,
                "Espo-Authorization-By-Token": "true"}
            # Use data instead of json to ensure exact body string matches signature
            response = requests.post(URL, data=body_string, headers=headers)   
            print(f"Response status code: {response.status_code}")

            # Check if the request was successful
            try:
                json_response = response.json()
            except:
                json_response = {"error": response.text}
            
            if response.status_code == 200:
                print("Success! CRM Response:", json_response)
                return json_response, response.status_code
            else:
                print(f"CRM API returned non-200 status: {response.status_code}")
                print("Error response:", json_response)
                return json_response, response.status_code
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"success": False, "detail": str(e)}, 500
    
    return {"success": False, "detail": "An unknown error occurred"}, 500 
