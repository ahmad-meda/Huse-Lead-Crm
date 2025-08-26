from proxies.lead_proxy import LeadProxy
from Utils.ai_client import client
from dotenv import load_dotenv
from HelperAgents.name_selection import choose_name
from Utils.agents import get_lead_update_details, extract_data_to_update
from Utils.update_lead_states import update_lead_states  
from Utils.choices import LeadChoices
from Utils.fuzzy_logic import find_best_match


load_dotenv()

def update_lead_status(messages: list, agent_phone_number: str):
    """
    Update the lead details in the CRM Backend
    """

    agent_id = LeadProxy.to_get_employee_database_id_by_contact(agent_phone_number)
    

    fields_to_ask = update_lead_states.main_fields

    lead_status_given = False
    user_identified = False
    while True:

        user_input = input("User: ")
        messages.append({"role": "user", "content": user_input})
        if user_input.lower() == "exit":
            break

        # Pass only the last 2 messages to the extract_data_to_update function
        extracted_data = extract_data_to_update(messages[-2:], fields_to_ask)

        if extracted_data.lead_status:
            membership_tier = find_best_match(user_input=extracted_data.lead_status, choices=LeadChoices.get_lead_status_choices())
            print(f"Debug - Membership tier: {membership_tier}")
            if membership_tier:
                extracted_data.lead_status = membership_tier
                lead_status_given = True
            else:
                print(f"Debug - No lead status found for {extracted_data.lead_status}")
                continue

        if not user_identified:

            if extracted_data.phone_number:
                print(f"Debug - Extracted phone: {extracted_data.phone_number}")
                member = LeadProxy.to_get_member_by_phone(phone_number=extracted_data.phone_number, agent_id=str(agent_id))
                print(f"Debug - Member: {member}")
                if member:
                    print(f"Debug - Member found: {member}")
                    lead_id = member.id
                    user_identified = True
                    print(f"Debug - Lead found: {member}")
                    print(f"Debug - Lead ID: {lead_id}")
                    #remove email, contact and full_legal_name from fields_to_ask
                    fields_to_ask = [field for field in fields_to_ask if field not in ["email_address", "contact_number", "full_legal_name"]]
                    user_identified = True
                else:
                    print(f"Debug - Lead not found: {extracted_data.phone_number}")
            elif extracted_data.email_address:
                print(f"Debug - Extracted email: {extracted_data.email_address}")
                member = LeadProxy.to_get_member_by_email(email_address=extracted_data.email_address, agent_id=str(agent_id))
                if member != None:
                    print(f"Debug - Member found: {member}")
                    lead_id = member.id
                    user_identified = True
                    print(f"Debug - Lead found: {member}")
                    print(f"Debug - Lead ID: {lead_id}")
                    #remove phone_number, contact and full_legal_name from fields_to_ask
                    fields_to_ask = [field for field in fields_to_ask if field not in ["phone_number", "contact_number", "full_legal_name"]]
                    user_identified = True
            elif extracted_data.full_legal_name:
                print(f"Debug - Extracted name: {extracted_data.full_legal_name}")
                members = LeadProxy.to_get_members_by_name(name=extracted_data.full_legal_name, agent_id=str(agent_id))
                print(f"Debug - Members found: {members}")
                
                if len(members) == 1:
                    # Single member found
                    member = members[0]  # Get the first (and only) member from the list
                    print(f"Debug - Single member found: {member}")
                    lead_id = member.id
                    user_identified = True
                    print(f"Debug - Lead found: {member}")
                    print(f"Debug - Lead ID: {lead_id}")
                    #remove phone_number, email_address and contact from fields_to_ask
                    fields_to_ask = [field for field in fields_to_ask if field not in ["phone_number", "email_address", "contact_number"]]
                    user_identified = True
                    
                elif len(members) > 1:
                    # Multiple members found
                    print(f"Debug - Multiple members found: {len(members)} members")
                    try:
                        messages, name_chosen = choose_name(members=members, messages=messages)
                        print(f"Debug - Name chosen: {name_chosen}")
                        
                        # Find the specific member from the original list that matches the chosen name
                        chosen_member = None
                        for m in members:
                            if m.full_legal_name == name_chosen or str(m.full_legal_name).lower() == str(name_chosen).lower():
                                chosen_member = m
                                break
                        
                        if chosen_member:
                            lead_id = chosen_member.id
                            user_identified = True
                            print(f"Debug - Selected member: {chosen_member}")
                            print(f"Debug - Lead ID: {lead_id}")
                            #remove phone_number, email_address and contact from fields_to_ask
                            fields_to_ask = [field for field in fields_to_ask if field not in ["phone_number", "email_address", "contact_number"]]
                            user_identified = True
                        else:
                            print(f"Debug - Could not find member with name: {name_chosen}")
                            
                    except Exception as e:
                        print(f"Debug - Error in name selection: {e}")
                        
                else:
                    # No members found
                    print(f"Debug - No members found with name: {extracted_data.full_legal_name}")


        if lead_status_given and user_identified:
            LeadProxy.to_update_lead_status(member_id=lead_id, new_lead_status=extracted_data.lead_status)
            fields_to_ask = []
            return lead_id
        
        
        response = get_lead_update_details(messages, fields_to_ask)
        messages.append({"role": "assistant", "content": response.message_to_user})
        print(f"Assistant: {response.message_to_user}")

# Test the function
update_lead_status(messages=[], agent_phone_number="+971 8751876398")