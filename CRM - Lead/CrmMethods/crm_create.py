import json
import requests
from proxies.lead_proxy import LeadProxy
from datetime import datetime
from CrmMethods.crm_dictionary import build_crm_payload

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
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic{crm_token}",
                "espo-authorization": crm_token,
                "Espo-Authorization-By-Token": "true"}
            response = requests.post(URL, json=payload)   
            print(f"Response status code: {response.status_code}")

            # Check if the request was successful
            if response.status_code == 200:
                json_response = response.json()
                print("Success! CRM Response:", json_response)
                return json_response
            else:
                print(f"CRM API returned non-200 status: {response.status_code}")
                try:
                    error_response = response.json()
                    print("Error response:", error_response)
                except:
                    print("Error response (raw):", response.text)
                return {"success": False, "detail": "CRM API returned non-200 status"}
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"success": False, "detail": str(e)}
    
    return {"success": False, "detail": "An unknown error occurred"} , 