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
from proxies.lead_session_proxy import LeadSessionProxy

# Define a Pydantic model for the request body
class LeadRequest(BaseModel):
    full_legal_name: str
    phone_number: str
    email_address: str
    suggested_membership_tier: str
    company: str
    lead_status: str


def add_lead_in_crm(contact_number:str, full_name:str, phone_number:str, email_address:str, suggested_membership_tier:str, company:str, lead_status: str):
    try:
        # Validate input parameters
        if not contact_number:
            raise ValueError("Contact number is required")
        if not full_name:
            raise ValueError("Full name is required")
        if not phone_number:
            raise ValueError("Phone number is required")
        if not email_address:
            raise ValueError("Email address is required")
        if not suggested_membership_tier:
            raise ValueError("Suggested membership tier is required")
        if not company:
            raise ValueError("Company is required")
        if not lead_status:
            raise ValueError("Lead status is required")

        # Get the Sales Agent ID from the database using the contact number
        try:
            agent_id = LeadProxy.to_get_employee_database_id_by_contact(contact_number=contact_number)
            print(f"Employee Database ID: {agent_id}")
        except Exception as e:
            print(f"Error retrieving agent ID: {str(e)}")
            raise Exception(f"Failed to retrieve agent information: {str(e)}")

        if agent_id is None:
            raise ValueError("No agent found for the contact number")

        # Get CRM Token
        try:
            crm_token = LeadProxy._get_crm_token_by_employee_database_id(employee_database_id=agent_id)
            print(f"CRM Token: {crm_token}")
        except Exception as e:
            print(f"Error retrieving CRM token: {str(e)}")
            raise Exception(f"Failed to retrieve CRM token: {str(e)}")
        
        if crm_token is None:
            raise ValueError("No CRM Token found for the agent")

        # Checks if there is draft Present in the database or else create a new one, this will be edited
        try:
            draft_id, existed, null_fields = LeadProxy.to_get_or_create_draft(agent_id=str(agent_id))
            print(f"Draft ID: {draft_id}, Was existing: {existed}, Null fields: {null_fields}")
        except Exception as e:
            print(f"Error creating/retrieving draft: {str(e)}")
            raise Exception(f"Failed to create or retrieve draft: {str(e)}")

        # Add the extracted data to the database
        # Create a LeadData object with the provided information
        extracted_data = LeadRequest(
            full_legal_name=full_name,
            phone_number=phone_number,
            email_address=email_address,
            suggested_membership_tier=suggested_membership_tier,
            company=company,
            lead_status=lead_status)
        print(f"Extracted data: {extracted_data}")
        
        try:
            LeadProxy.to_update_draft(
                draft_id=draft_id, 
                extracted_data=extracted_data
            )
        except Exception as e:
            print(f"Error updating draft: {str(e)}")
            raise Exception(f"Failed to update draft with lead data: {str(e)}")

        # Create lead in CRM
        try:
            crm_success = crm_create_lead(lead_id=draft_id, crm_token=crm_token)
        except Exception as e:
            print(f"Error creating lead in CRM: {str(e)}")
            raise Exception(f"Failed to create lead in CRM: {str(e)}")

        # Complete the draft if CRM creation was successful
        try:
            if not crm_success.get("failure"):  
                LeadProxy.to_complete_draft(draft_id=draft_id)
        except Exception as e:
            print(f"Error completing draft: {str(e)}")
            # Don't raise here as the lead was created successfully in CRM
            print("Warning: Lead created in CRM but failed to mark draft as complete")

        return crm_success

    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return {"failure": True, "error": f"Validation error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error in add_lead: {str(e)}")
        return {"failure": True, "error": f"Unexpected error: {str(e)}"}
