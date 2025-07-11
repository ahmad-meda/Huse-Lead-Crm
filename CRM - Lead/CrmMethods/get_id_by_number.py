import requests
import json

def get_lead_id_by_phone(phone_number):
   URL = "http://16.24.199.255/api/v1/Lead"
   headers = {
       "accept": "*/*",
       "espo-authorization": "YWRtaW46YWRtaW5AMTIz"
   }
   
   try:
       # Fetch all leads
       response = requests.get(URL, headers=headers)
       
       if response.status_code == 200:
           data = response.json()
           leads = data.get('list', [])
           
           # Search for lead with matching phone number
           for lead in leads:
               # Check primary phone number
               if lead.get('phoneNumber') == phone_number:
                   return lead.get('id')
               
               # Also check in phoneNumberData array
               phone_data = lead.get('phoneNumberData', [])
               for phone_entry in phone_data:
                   if phone_entry.get('phoneNumber') == phone_number:
                       return lead.get('id')
                       
               # Check other phone fields that might contain the number
               if (lead.get('cPaMobileNumber') == phone_number or 
                   lead.get('cBusinessPhone') == phone_number or
                   lead.get('cLandlineNumber') == phone_number):
                   return lead.get('id')
           
           # No lead found
           return None
           
       else:
           print(f"Error: HTTP {response.status_code}")
           return None
           
   except requests.exceptions.RequestException as e:
       print(f"Request failed: {e}")
       return None

def get_lead_number_by_id(lead_id):
    URL = f"http://16.24.199.255/api/v1/Lead/{lead_id}"
    headers = {
        "accept": "*/*",
        "espo-authorization": "YWRtaW46YWRtaW5AMTIz"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('phoneNumber')
    else:
        print(f"Error: HTTP {response.status_code}")
        return None
    
# Example usage:
# lead_number = get_lead_number_by_id("68626fb435d303b23")
# if lead_number:
#    print(f"Lead Number: {lead_number}")
# else:
#    print("Lead not found")