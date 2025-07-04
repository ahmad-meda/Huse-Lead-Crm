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

db = SessionLocal()


def add_lead(messages: List[dict], contact_number:int) -> dict:
 

    """ When this bot is taking over from the main bot, we will 
    if the user has provided any details in the message """

    # Get the Sales Agent ID from thedatabase using the contact number
    agent_id = LeadProxy.to_get_employee_database_id_by_contact(contact_number=contact_number)
    print(f"Employee Database ID: {agent_id}")

    # Checks if there is draft Present in the database or else create a new one,this will be edited

    draft_id, existed, null_fields = LeadProxy.to_get_or_create_draft(agent_id=agent_id)
    print(f"Draft ID: {draft_id}, Was existing: {existed}, Null fields: {null_fields}")

    # If the draft is already present, we remove the fields that are not null so that we can pass only the relevant fields to the bot to ask the user.
    if null_fields:
        main_fields = [field for field in agent_states.main_fields if field in null_fields]
        secondary_fields = [field for field in agent_states.secondary_fields if field in null_fields]
        optional_job_fields = [field for field in agent_states.optional_job_fields if field in null_fields]
        optional_education_fields = [field for field in agent_states.optional_education_fields if field in null_fields]


    # Check what lists are not empty and set the current field to ask the user
    current_field = None
    
    if main_fields:
        current_field = main_fields
    elif secondary_fields:
        current_field = secondary_fields
    elif optional_job_fields:
        current_field = optional_job_fields
    elif optional_education_fields:
        current_field = optional_education_fields
    else:
        print("")

    lead_status_given = False
    membership_tier_given = False

    # Now we start the main loop to ask the user for the details
    while True:

        if existed is True:
            # Get all filled details in one variable
            filled_details = LeadProxy.to_get_draft_by_id(draft_id)
            
            print(filled_details)

            # Parse the filled details into a readable format
            if filled_details:
                details_text = "Current Details: --\n\n"
                
                # Create a mapping for better field names
                field_names = {
                    'full_legal_name': 'Full Legal Name',
                    'preferred_nickname': 'Preferred Nickname',
                    'date_of_birth': 'Date of Birth',
                    'nationality': 'Nationality',
                    'phone_number': 'Phone Number',
                    'email_address': 'Email Address',
                    'suggested_membership_tier': 'Suggested Membership Tier',
                    'residential_address': 'Residential Address',
                    'passport_number': 'Passport Number',
                    'id_number': 'ID Number',
                    'occupation': 'Occupation',
                    'job_title': 'Job Title',
                    'linkedin_or_website': 'LinkedIn/Website',
                    'education_background': 'Education Background',
                    'notable_affiliations': 'Notable Affiliations',
                    'status': 'Status',
                    'lead_status': 'Lead Status',
                    'lead_comments': 'Lead Comments'
                }
                
                for field, value in filled_details.items():
                    if field not in ['id', 'status', 'agent_id']:  # Skip the ID and status and agent_id fields
                        display_name = field_names.get(field, field.replace('_', ' ').title())
                        details_text += f"• {display_name}: {value}\n"
                
                message_content = f"It seems like there is a draft in progress!\n\n{details_text}\nWould you like to continue filling it out or start fresh?"
            else:
                message_content = "It seems like there is a draft in progress, but no details were found. Would you like to start fresh?"

            print(f"Assistant: {message_content}")
            messages.append({
                "role": "assistant",
                "content": message_content
            })
            existed = False  # Reset existed to False after showing the message
            
        if messages and messages[-1]['role'] == 'user':
            print("Last message was from user, skipping user input.")
        else:
            user_input = input("User:")
            messages.append({
                "role": "user",
                "content": user_input
            })
            if if_user_wants_to_refresh_draft(messages):
                LeadProxy.to_clear_draft_fields(draft_id)

                # RESET ALL THE FIELD LISTS to original values
                main_fields = agent_states.main_fields
                secondary_fields = agent_states.secondary_fields
                optional_job_fields = agent_states.optional_job_fields
                optional_education_fields = agent_states.optional_education_fields
                
                # Reset current_field
                current_field = main_fields
                continue
        extracted_data = extract_data(messages)

        if extracted_data.lead_status:
            membership_tier = find_best_match(user_input=extracted_data.lead_status, choices=LeadChoices.get_lead_status_choices())
            print(f"Debug - Membership tier: {membership_tier}")
            if membership_tier:
                extracted_data.lead_status = membership_tier
                lead_status_given = True
            else:
                print(f"Debug - No lead status found for {extracted_data.lead_status}")
        if extracted_data.suggested_membership_tier:
            membership_tier = find_best_match(user_input=extracted_data.membership_tier, choices=LeadChoices.get_membership_choices())
            print(f"Debug - Membership tier: {membership_tier}")
            if membership_tier:
                extracted_data.membership_tier = membership_tier
                membership_tier_given = True
            else:
                print(f"Debug - No membership tier found for {extracted_data.membership_tier}")

        # Update the draft with the extracted data
        LeadProxy.to_update_draft(draft_id, extracted_data)

        filled_fields = []
        for field_name in ['full_legal_name', 'preferred_nickname', 'phone_number', 'email_address', 
                        'date_of_birth', 'nationality', 'suggested_membership_tier', 'residential_address', 
                        'passport_number', 'id_number', 'occupation', 'job_title', 'linkedin_or_website', 
                        'education_background', 'notable_affiliations', 'lead_comments']:
            field_value = getattr(extracted_data, field_name)
            if field_value and field_value.strip():  # Check if field has actual content
                filled_fields.append(field_name)

        # Update all field lists by removing filled fields
        main_fields = [field for field in main_fields if field not in filled_fields]
        secondary_fields = [field for field in secondary_fields if field not in filled_fields]
        optional_job_fields = [field for field in optional_job_fields if field not in filled_fields]
        optional_education_fields = [field for field in optional_education_fields if field not in filled_fields]

        # UPDATE current_field to reflect the changes
        if main_fields:
            current_field = main_fields
        elif secondary_fields:
            current_field = secondary_fields
        elif optional_job_fields:
            current_field = optional_job_fields
        elif optional_education_fields:
            current_field = optional_education_fields
        else:
            current_field = []


        if current_field == main_fields and main_fields:
            missing_fields = [field for field in current_field if not getattr(extracted_data, field)]
            if missing_fields:
                response = get_lead_details(messages, current_field)
                output = response.message_to_user
                if "lead status" in response.message_to_user:
                    output += "\nThe status of the lead can be Hot, Cold or Warm"
                
                messages.append({"role": "assistant", "content": output})
                print(f"Assistant: {output}")
                continue
            else:
                current_field = secondary_fields if secondary_fields else (optional_job_fields if optional_job_fields else optional_education_fields)
                if current_field:  # Only proceed if there are fields to fill
                    response = get_lead_details(messages, current_field)
                    messages.append({"role": "assistant", "content": response.message_to_user})
                    print(f"Assistant: {response.message_to_user}")
                continue
        elif current_field == secondary_fields and secondary_fields:
            missing_fields = [field for field in current_field if not getattr(extracted_data, field)]
            if missing_fields:
                response = get_lead_details(messages, current_field)
                messages.append({"role": "assistant", "content": response.message_to_user}) 
                print(f"Assistant: {response.message_to_user}")
                continue
            else:
                current_field = optional_job_fields if optional_job_fields else optional_education_fields
                if current_field:  # Only proceed if there are fields to fill
                    response = get_lead_details(messages, current_field)
                    messages.append({"role": "assistant", "content": response.message_to_user})
                    print(f"Assistant: {response.message_to_user}")
                continue
        elif current_field == optional_job_fields:
            print("Optional Job Fields")
            skipped = skipped_lead_details(messages, current_field).fields_the_user_wants_to_skip
            print(f"Skipped: {skipped}")
            
            # If user skipped specific fields, check if they want to skip ALL remaining as well
            # Only call check_skip_all_optional if they didn't already specify field-level skipping
            skip_all_optional = False
            if not skipped:  # Only check for skip-all if no specific fields were skipped
                skip_all_optional = check_skip_all_optional(messages)

            if skip_all_optional:
                print("Congrats!! You are officially our member!")
                return LeadProxy.to_complete_draft(draft_id), draft_id

            # Check if all job fields are either filled or skipped
            fields_to_check = [field for field in current_field if field not in skipped]
            missing_fields = [field for field in fields_to_check if not getattr(extracted_data, field)]
            
            if missing_fields:
                response = get_lead_details(messages, current_field)
                messages.append({"role": "assistant", "content": response.message_to_user}) 
                print(f"Assistant: {response.message_to_user}")
                continue
            else:
                # All job fields are done (filled or skipped), move to education fields
                current_field = optional_education_fields
                if current_field:  # Only proceed if there are education fields to fill
                    response = get_lead_details(messages, current_field)
                    messages.append({"role": "assistant", "content": response.message_to_user})
                    print(f"Assistant: {response.message_to_user}")
                    continue
                else:
                    # No education fields to fill, complete the draft
                    print("All fields completed!")
                    return LeadProxy.to_complete_draft(draft_id), draft_id
        elif current_field == optional_education_fields:
            skipped = skipped_lead_details(messages, current_field).fields_the_user_wants_to_skip
            skip_all_optional = check_skip_all_optional(messages)
            
            if skip_all_optional:
                print("Congrats!! You are officially our member!")
                return LeadProxy.to_complete_draft(draft_id), draft_id
            
            fields_to_check = [field for field in current_field if field not in skipped]
            missing_fields = [field for field in fields_to_check if not getattr(extracted_data, field)]

            if missing_fields:
                response = get_lead_details(messages, current_field)
                messages.append({"role": "assistant", "content": response.message_to_user})
                print(f"Assistant: {response.message_to_user}")
                continue
            else:
                print("All fields completed!")
                return LeadProxy.to_complete_draft(draft_id), draft_id
    
#Test
add_lead(messages=[], contact_number="+971 8751876398")