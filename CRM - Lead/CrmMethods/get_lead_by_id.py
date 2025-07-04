import requests
from dotenv import load_dotenv
import os

load_dotenv()

def get_lead_by_id(lead_id):    # this is the lead id of the lead that we want to update
        URL = f"https://guest-app-api.therufescent.com/api/leads/crm/get_lead/{lead_id}"
        headers = {
            "accept": "*/*",
            "espo-authorization": os.getenv("ESPO_AUTHORIZATION")
        }

        try:
            # Fetch specific lead by ID
            response = requests.get(URL, headers=headers)
            
            if response.status_code == 200:
                lead_data = response.json()
                return lead_data
                
            elif response.status_code == 404:
                print(f"Lead with ID {lead_id} not found")
                return None
                
            else:
                print(f"Error: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None