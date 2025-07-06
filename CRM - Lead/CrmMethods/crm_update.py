import json
import requests
import os 
import dotenv
from proxies.lead_proxy import LeadProxy
from update_lead import update_lead_status
from CrmMethods.get_id_by_number import get_lead_id_by_phone
dotenv.load_dotenv()    


def update_crm_lead_status(db_lead_id: str):

    # Get the phone number from the database based on the id
    phone_number = LeadProxy.to_get_member_id_by_phone(db_lead_id)
    lead_id = get_lead_id_by_phone(phone_number)    #this is the lead id of the lead that we want to update
    lead_details = LeadProxy.to_get_complete_by_id(complete_id=int(db_lead_id))

    # API endpoint for updating lead
    URL = f"http://16.24.199.255/api/v1/Lead/{lead_id}"

    # Headers according to the documentation
    headers = {
        "Content-Type": "application/json",
        "espo-authorization": "YWRtaW46YWRtaW5AMTIz"
    }

    # Data to update - only status field
    update_data = {
         "cLeadStatus": lead_details.get("lead_status")
    }

    # Print the update data
    print("Update Data JSON:", json.dumps(update_data, indent=2))
    # print(f"Updating lead ID: {lead_id}")

    try:
        # Send PUT request to update the lead
        response = requests.put(URL, json=update_data, headers=headers)
        
        
        print(f"Response Status Code: {response.status_code}")

        
        if response.status_code == 200:
            print("Lead updated successfully!")
            print("Response:", response.json())

        else:
            print(f"Failed to update lead. Status code: {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")