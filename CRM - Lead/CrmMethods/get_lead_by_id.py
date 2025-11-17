import requests
import json
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
                # Validate response is JSON
                try:
                    lead_data = response.json()
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Response text: {response.text}")
                    return None
                
                # Ensure we return a dict (or None if invalid)
                if not isinstance(lead_data, dict):
                    print(f"Warning: Response is not a dict, got {type(lead_data).__name__}")
                    return None
                
                return lead_data
                
            elif response.status_code == 404:
                print(f"Lead with ID {lead_id} not found")
                return None
                
            else:
                print(f"Error: HTTP {response.status_code}")
                try:
                    error_text = response.text
                    print(f"Error response: {error_text}")
                except:
                    pass
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
