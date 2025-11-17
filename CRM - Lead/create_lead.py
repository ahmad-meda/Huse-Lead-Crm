import os
import dotenv
from pydantic import BaseModel
from typing import Optional, List
from Utils.add_lead_states import agent_states
from proxies.lead_proxy import LeadProxy
from Utils.agents import get_lead_details, extract_data, if_user_wants_to_refresh_draft, skipped_lead_details, check_skip_all_optional
from Files.SQLAlchemyModels import SessionLocal
from Utils.choices import LeadChoices
from Utils.fuzzy_logic import find_best_match
from Utils.current_field import remove_used_fields_and_return_next, remove_fields_by_name_and_return_next
from CrmMethods.crm_create import crm_create_lead

def add_lead(messages: List[dict], contact_number:str):

    # Get the Sales Agent ID from thedatabase using the contact number
    agent_id = LeadProxy.to_get_employee_database_id_by_contact(contact_number=contact_number)
    print(f"Employee Database ID: {agent_id}")

    # Checks if there is draft Present in the database or else create a new one,this will be edited
    draft_id, existed, null_fields = LeadProxy.to_get_or_create_draft(agent_id=str(agent_id))
    # print(f"Draft ID: {draft_id}, Was existing: {existed}, Null fields: {null_fields}")

    # If the draft is already present, we remove the fields that are not null so that we can pass only the relevant fields to the bot to ask the user.
    if null_fields:
        main_fields = [field for field in agent_states.main_fields if field in null_fields]
        secondary_fields = [field for field in agent_states.secondary_fields if field in null_fields]
        optional_job_fields = [field for field in agent_states.optional_job_fields if field in null_fields]
        optional_education_fields = [field for field in agent_states.optional_education_fields if field in null_fields]
    
    while True:

        user_input = input("User: ") # Start with user Input
        messages.append({"role": "user", "content": user_input}) # add it to history

        lead_record = LeadProxy.get_lead_record(lead_id=draft_id)

        # Convert lead record to dictionary for LLM
        lead_record_dict = {
            "full_legal_name": lead_record.full_legal_name,
            "preferred_nickname": lead_record.preferred_nickname,
            "date_of_birth": lead_record.date_of_birth,
            "nationality": lead_record.nationality,
            "phone_number": lead_record.phone_number,
            "email_address": lead_record.email_address,
            "lead_status": lead_record.lead_status,
            "suggested_membership_tier": lead_record.suggested_membership_tier,
            "residential_address": lead_record.residential_address,
            "passport_number": lead_record.passport_number,
            "id_number": lead_record.id_number,
            "occupation": lead_record.occupation,
            "job_title": lead_record.job_title,
            "linkedin_or_website": lead_record.linkedin_or_website,
            "education_background": lead_record.education_background,
            "notable_affiliations": lead_record.notable_affiliations,
            "lead_comments": lead_record.lead_comments,
            "company": lead_record.company
        }

        print(f"Lead record dictionary: {lead_record_dict}")
        extracted_data = extract_data(messages=messages, list_of_fields=lead_record_dict)

        extracted_data = extract_data(messages=messages) # extract whatever fields are mentioned, this will extract whetevr fields are given by the user regardless of what the bot has asked.
        # print(extracted_data)

        if extracted_data.lead_status or extracted_data.suggested_membership_tier or extracted_data.nationality: # fuzzy logic for fields (lead_status, suggested_membership_tier, nationality)
            extracted_data.lead_status = find_best_match(user_input=extracted_data.lead_status, choices=LeadChoices.get_lead_status_choices())
            extracted_data.suggested_membership_tier = find_best_match(user_input=extracted_data.suggested_membership_tier, choices=LeadChoices.get_membership_choices())
            extracted_data.nationality = find_best_match(user_input=extracted_data.nationality, choices=LeadChoices.get_country_choices())

        # add the extracted data to the database
        LeadProxy.to_update_draft(draft_id=draft_id, extracted_data=extracted_data)

        current_field, remaining_fields = remove_used_fields_and_return_next(data_object=extracted_data,main_fields=main_fields,secondary_fields=secondary_fields,optional_job_fields=optional_job_fields,optional_education_fields=optional_education_fields)
        
        print(f"current field: {current_field}")
        if current_field is None and len(remaining_fields) == 0: #When all fields have been asked # Change the status of the lead to New.
            crm_token = LeadProxy._get_crm_token_by_employee_database_id(employee_database_id=agent_id)
            try:
                crm_success = crm_create_lead(lead_id=draft_id, crm_token=crm_token) # After all the fields are given to the user, we create a new lead in the CRM  Backend.
            except Exception as e:
                print(f"Error creating lead in CRM: {str(e)}")
                print(f"Unexpected error occurred while adding lead: {str(e)}")
                user_message = f"Failed to create lead in CRM due to error."
                send_whatsapp_message(contact_number, user_message)
                return False
            
            # Validate that crm_success is a dictionary
            if not isinstance(crm_success, dict):
                error_msg = f"Invalid response type from CRM: expected dict, got {type(crm_success).__name__}. Response: {str(crm_success)}"
                print(f"Error: {error_msg}")
                print(f"Unexpected error occurred while adding lead: {error_msg}")
                user_message = f"Failed to create lead in CRM due to error."
                send_whatsapp_message(contact_number, user_message)
                return False
            
            # Check if the 'failure' key is False or absent (indicating success)
            if not crm_success.get("failure", False):
                LeadProxy.to_complete_draft(draft_id=draft_id)
                # print("Lead created successfully in CRM")
                return True
            else:
                error_msg = crm_success.get("error") or crm_success.get("detail") or "Unknown error from CRM"
                print(f"Failed to create lead in CRM: {error_msg}")
                print(f"Unexpected error occurred while adding lead: {error_msg}")
                user_message = f"Failed to create lead in CRM due to error."
                send_whatsapp_message(contact_number, user_message)
                return False
            # else:
            #     print("Failed to create lead in CRM, trying again")
            #     continue

        # print(f"current field: {current_field}")
        # print(f"remaining fields: {remaining_fields}")
        # Pass only the last 2 messages to the agent
        response = get_lead_details(messages=messages,fields=remaining_fields)
        messages.append({"role": "assistant", "content": response.message_to_user})
        print(f"Assistant: {response.message_to_user}")
        continue


#test code

add_lead(messages=[], contact_number="+971509565289")
