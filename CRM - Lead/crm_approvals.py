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
        
        # Debug: Print what was extracted
        print(f"Debug - Extracted data: Approve={extracted_data.Approve}, Reject={extracted_data.Reject}, Flag={extracted_data.Flag}, Waitlist={extracted_data.Waitlist}")
        
        # Check for clear decisions first
        if extracted_data.Approve:
            print("[DEBUG] ✅ Approved")
            result = LeadProxy.to_update_conversion_status(member_id=lead_db_id, conversion_status="Approved")
            #update the approval status to approved
            LeadProxy.to_update_member_approval_status(member_id=lead_db_id, approval_status="Completed")
            print(result)
            # Update in the crm as well
            print(update_approval_status(crm_lead_id=crm_lead_id, approval_status="approved"))
            

            break
        elif extracted_data.Reject:
            print("[DEBUG] ❌ Rejected")
            result = LeadProxy.to_update_conversion_status(member_id=lead_db_id, conversion_status="Rejected")
            #update the approval status to rejected
            LeadProxy.to_update_member_approval_status(member_id=lead_db_id, approval_status="Completed")
            update_approval_status(crm_lead_id=crm_lead_id, approval_status="rejected")
            print(result)
            break
        elif extracted_data.Flag:
            print("[DEBUG] 🚩 Flagged")
            result = LeadProxy.to_update_conversion_status(member_id=lead_db_id, conversion_status="Flagged")
            #update the approval status to flagged
            LeadProxy.to_update_member_approval_status(member_id=lead_db_id, approval_status="Completed")
            update_approval_status(crm_lead_id=crm_lead_id, approval_status="flagged")
            print(result)
            break
        elif extracted_data.Waitlist:
            print("[DEBUG] ⏳ Waitlisted")
            result = LeadProxy.to_update_conversion_status(member_id=lead_db_id, conversion_status="Waitlisted")
            #update the approval status to waitlisted
            LeadProxy.to_update_member_approval_status(member_id=lead_db_id, approval_status="Completed")
            update_approval_status(crm_lead_id=crm_lead_id, approval_status="waitlisted")
            print(result)
            break
        else:
            # No clear decision made, get bot response
            print("[DEBUG]🤖 No clear decision detected, getting bot response...")
            
            try:
                response = lead_state_allocation_agent(messages)
                bot_message = response.message_to_user
                print(f"Bot: {bot_message}")
                
                # Add bot response to conversation history
                messages.append({
                    "role": "assistant",
                    "content": bot_message
                })
                
            except Exception as e:
                print(f"Error getting bot response: {e}")
                print("Please try again with: Approve, Reject, Flag, or Waitlist")




insert_lead_value(crm_lead_id="686619785bac67324")