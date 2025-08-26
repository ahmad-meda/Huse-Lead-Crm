import json
import requests
from proxies.lead_proxy import LeadProxy
from datetime import datetime

def crm_create_lead(lead_id: str):
    # Get the lead details from the draft id
    lead_details = LeadProxy.to_get_complete_by_id(complete_id=lead_id)
    print("Lead details:", lead_details)

    # Check if lead_details is None
    if lead_details is None:
        print(f"Error: No lead found with ID {lead_id} or database connection issue")
        exit(1)

    URL = "https://guest-app-api.therufescent.com/api/leads/crm/create_lead"


    if lead_details is not None:
        # Parse the full name into first and last name
        full_name = lead_details.get('full_legal_name', '')
        name_parts = full_name.split() if full_name else []
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Get current date for application date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Format email data
        email = lead_details.get('email_address', '')
        email_data = []
        if email:
            email_data = [{
                "emailAddress": email,
                "primary": True,
                "optOut": False,
                "invalid": False,
                "lower": email.lower()
            }]
        
        # Format phone data
        phone = lead_details.get('phone_number', '')
        phone_data = []
        if phone:
            phone_data = [{
                "phoneNumber": phone,
                "primary": True,
                "type": "Mobile",
                "optOut": False,
                "invalid": False
            }]


        crm_data = {
            "status": lead_details.get('status', 'New'),
            "cApplicationDate": current_date,
            "cMembershipCategory": lead_details.get('suggested_membership_tier', ''),
            "cNationality": lead_details.get('nationality', ''),
            "cPaymentsMembershipCategory": lead_details.get('suggested_membership_tier', ''),
            "firstName": first_name,
            "lastName": last_name,
            "name": full_name,
            "cPreferredName": lead_details.get('preferred_nickname', ''),
            "cDateOfBirth": lead_details.get('date_of_birth', ''),
            "cIdNumber": lead_details.get('id_number', ''),
            "emailAddressData": email_data,
            "emailAddress": email,
            "emailAddressIsOptedOut": False,
            "emailAddressIsInvalid": False,
            "phoneNumberData": phone_data,
            "phoneNumber": phone,
            "phoneNumberIsOptedOut": False,
            "phoneNumberIsInvalid": False,
            "cFullName": full_name,
            "cLeadStatus": lead_details.get('lead_status', ''),
            "cJobTitle": lead_details.get('job_title', ''),
            "cJobTitle3": lead_details.get('job_title', ''),
            "cEmailAddress": email,
            "cPaMobileNumber": phone,
            "cStreetAddressStreet": lead_details.get('residential_address', ''),
            "cApplicantsName": full_name,
            "assignedUserName": None,
            "assignedUserId": None,  # Set to None instead of agent_id to avoid the user error
            "teamsIds": [],
            "teamsNames": {}
        }
        
        # Print the JSON data that will be sent
        print("CRM Data JSON:", json.dumps(crm_data, indent=2))

        try:

            response = requests.post(URL, json={"data": crm_data})   
            print(response.status_code)

            json_response = response.json()
            print(json_response)
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")