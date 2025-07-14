import requests
import json
from Utils.agents import extracted_data_for_lead_state_allocation, lead_state_allocation_agent
from proxies.lead_proxy import LeadProxy
from CrmMethods.update_approval_status import update_approval_status
from CrmMethods.get_lead_by_id import get_lead_by_id
from CrmMethods.display_lead_details import display_lead_details
from CrmMethods.get_id_by_number import get_lead_number_by_id

""" To test the function, use the following lead id: 686619785bac67324 """

def insert_lead_value(crm_lead_id: str):
    
    URL = f"https://guest-app-api.therufescent.com/api/leads/crm/get_lead/{crm_lead_id}"
    headers = {
        "accept": "*/*",
        "espo-authorization": "YWRtaW46YWRtaW5AMTIz"
    }
        
    # CHECK IS THE LEAD IS ALREADY APPROVED, REJECTED, FLAGGED, WAITLISTED
    response = requests.get(URL, headers=headers)
    print(response.json())
    data = response.json()
    lead_number = get_lead_number_by_id(crm_lead_id)
    lead_db_id = LeadProxy.to_get_member_id_by_phone(lead_number)
    print(crm_lead_id)
    print(lead_number)
    print(lead_db_id)
    approval_status_crm = data.get('data').get('cApprovalStatus')
    approval_status_db = LeadProxy.to_get_member_approval_status(member_id=lead_db_id)


    # CHECK IF THE APPROVAL STATUS IS PENDING IN THE HUSE DB AND THE CRM BACKEND
    if approval_status_crm and approval_status_db != "Pending":
        print("Lead is already converted")
        return True

    # Get the lead details from the CRM backend
    lead_data = get_lead_by_id(crm_lead_id)
    display_lead_details(lead_data)

    #send messages to the all the sales agents in the aprroval table
    sales_agents = LeadProxy.to_get_active_approvers()
    print(sales_agents)

    main_message = "Here are the lead details, Do you want to Approve, Reject, Flag or Waitlist this lead?"
    messages = [
        {
            "role": "user",
            "content": main_message
        }
    ]
    print(main_message)
    # Loop to send messages to the sales agents
    for agent in sales_agents:
        print(f"[DEBUG] Sent message to {agent}")
    print(f"[DEBUG] Done: Sent messages to all sale agents!")
    print(f"[DEBUG] -Someone is reviewing the lead-")

    #Set the approval status from pending to In Progress
    LeadProxy.to_update_member_approval_status(member_id=lead_db_id, approval_status="In Progress")
    print(messages)
    while True:
        user_input = input("User: ")
        
        # Add user input to messages
        messages.append({
            "role": "user",     
            "content": user_input
        })
        #check is the conversion status is filled
        print(LeadProxy.to_check_conversion_status_filled(member_id=lead_db_id))
        found, has_valid_status, current_status = LeadProxy.to_check_conversion_status_filled(member_id=lead_db_id)
        print(found, has_valid_status, current_status)
        if has_valid_status is True:
            print("[DEBUG] Conversion status has already been filled")
            return True
        
        # Extract decision data
        extracted_data = extracted_data_for_lead_state_allocation(messages)
        
        






insert_lead_value(crm_lead_id="686619785bac67324")