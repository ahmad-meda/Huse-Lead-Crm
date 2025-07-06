import requests
from proxies.lead_proxy import LeadProxy


def update_approval_status(crm_lead_id, approval_status):
    url = f'https://guest-app-api.therufescent.com/api/leads/crm/update_approval_status/{crm_lead_id}?status={approval_status}'
    headers = {
        "accept": "*/*",
        "espo-authorization": "YWRtaW46YWRtaW5AMTIz"
    }
    response = requests.put(url)
    return response.json()

    
    