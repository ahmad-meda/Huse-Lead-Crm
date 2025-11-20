import datetime
import re
import country_converter as coco
import pycountry
from fuzzywuzzy import process, fuzz

from Files.WhatsAppSendAPIs import send_whatsapp_message, send_lead_status_menu, send_membership_tier_menu
from agents.leads.crm_integrations.crm_create import crm_create_lead
from agents.leads.utils.add_lead_states import agent_states
from agents.leads.utils.agents import get_lead_details, extract_data, skipped_lead_details, check_skip_all_optional
from agents.leads.utils.choices import LeadChoices
from agents.leads.utils.crm_validation_error import get_validation_error
from agents.leads.utils.current_field import remove_used_fields_and_return_next, remove_fields_by_name_and_return_next
from agents.leads.utils.fuzzy_logic import find_best_match
from proxy.lead_message_proxy import LeadMessageHistoryProxy
from proxy.lead_proxy import LeadProxy
from session.intent_session import clear_session


def as_str(val):
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    return str(val)

def sanitize_messages(msgs):
    # Only allow role and content, both as strings
    return [
        {
            "role": str(msg.get("role", "")),
            "content": str(msg.get("content", ""))
        }
        for msg in msgs
    ]

import re

# Unicode Bidi control characters, including LRE, PDF, etc.
BIDI_CONTROL_CHARS = ''.join([
    '\u202a',  # LRE
    '\u202b',  # RLE
    '\u202c',  # PDF
    '\u202d',  # LRO
    '\u202e',  # RLO
    '\u200e',  # LRM
    '\u200f',  # RLM
])

def strip_bidi_controls(s: str) -> str:
    return re.sub(f"[{re.escape(BIDI_CONTROL_CHARS)}]", "", s)



def add_lead(user_message, contact_number, session_id=None):
    """ When this bot is taking over from the main bot, we will 
    if the user has provided any details in the message """

    print("Entered Add lead")

    LeadMessageHistoryProxy.save_message(contact_number, "user", user_message, session_id)

    messages = LeadMessageHistoryProxy.get_message_history(contact_number, session_id)

    agent_id = LeadProxy.to_get_employee_database_id_by_contact(contact_number=contact_number)
    print(f"Employee Database ID: {agent_id}")

    # Checks if there is draft Present in the database or else create a new one,this will be edited

    draft_id, existed, null_fields = LeadProxy.to_get_or_create_draft(agent_id=agent_id)
    print(f"Draft ID: {draft_id}, Was existing: {existed}, Null fields: {null_fields}")

    # 5. Prepare field lists
    main_fields = [field for field in agent_states.main_fields if field in null_fields]
    secondary_fields = [field for field in agent_states.secondary_fields if field in null_fields]
    optional_job_fields = [field for field in agent_states.optional_job_fields if field in null_fields]
    optional_education_fields = [field for field in agent_states.optional_education_fields if field in null_fields]

    print("Main fields: ", main_fields)
    print("Secondary fields: ", secondary_fields)
    print("Optional fields: ", optional_job_fields)
    print("Optional education fields: ", optional_education_fields)

    print("About to extract data")

    extraction_messages = sanitize_messages(messages)
    extracted_data = extract_data(extraction_messages)
    print("Extracted data", extracted_data)

    if not is_valid_phone(extracted_data.phone_number):
        extracted_data.phone_number = None

    if extracted_data.phone_number:
        extracted_data.phone_number = strip_bidi_controls(extracted_data.phone_number)

    if extracted_data.lead_status or extracted_data.suggested_membership_tier or extracted_data.nationality:
        extracted_data.nationality = normalize_nationality(extracted_data.nationality)
        print(extracted_data.nationality)
        extracted_data.lead_status = find_best_match(user_input=extracted_data.lead_status,
                                                     choices=LeadChoices.get_lead_status_choices())
        extracted_data.suggested_membership_tier = find_best_match(user_input=extracted_data.suggested_membership_tier,
                                                                   choices=LeadChoices.get_membership_choices())
        extracted_data.nationality = find_best_match(user_input=extracted_data.nationality,
                                                     choices=LeadChoices.get_country_choices())
        print(extracted_data.nationality)

    result = LeadProxy.to_update_draft(draft_id, extracted_data)
    print("Result", result)

    error_string = ""
    try:
        if not result["success"]:
            error_string = ", ".join(result['errors'])
            print("Error Strings", error_string)
    except Exception as e:
        print("Exception", e)



    current_field, remaining_fields = remove_used_fields_and_return_next(data_object=extracted_data,
                                                                         main_fields=main_fields,
                                                                         secondary_fields=secondary_fields,
                                                                         optional_job_fields=optional_job_fields,
                                                                         optional_education_fields=optional_education_fields)

    print("Current fields", current_field)
    print("Remaining fields", remaining_fields)

    completed_draft = None
    if current_field is None and len(remaining_fields) == 0 and error_string == '':
        completed_draft = LeadProxy.to_complete_draft(draft_id)
        LeadMessageHistoryProxy.clear_message_history(contact_number, session_id)
        if completed_draft:
            try:
                print("Creating lead in CRM++++++++++++++")
                json, status_code = crm_create_lead(draft_id)
                form_link = json.get('lead_form_url')
                id = json.get('data', {}).get('id')
                print(id, "Id")
                print("form link", form_link)
                # 13. If all fields done, complete the lead and cleanup
                msg = (f"The lead has been successfully added to the CRM.\n\n You can view it at https://crm-dashboard.huse.ai/#Lead."
                    f"\n\nNeed to add more information? Just click the link below! You can also send this link to your lead so they can fill out their own details.\n\n {form_link}")

                lead_id = LeadProxy.assign_crm_backend_id(draft_id, id)
                print("CRM Backend id added", lead_id)

                is_success = (
                        status_code == 200 and
                        not json.get('failure', False)
                        and not (
                        "detail" in json and
                        json["detail"].get("messageTranslation", {}).get("label") == "validationFailure")
                )

                print("status_code:", status_code)
                print("json.get('failure', False):", json.get('failure', False))
                print("'detail' in json:", "detail" in json)

                if is_success:
                    LeadMessageHistoryProxy.save_message(contact_number, "assistant", msg, session_id)
                    send_whatsapp_message(contact_number, msg)
                    clear_session(contact_number)
                else:
                    LeadProxy.revert_status(draft_id)
                    label, field = None, None

                    if "detail" in json:
                        try:
                            label, field = get_validation_error(json)
                        except Exception as ex:
                            print(f"Failed to parse CRM validation error: {ex}")

                    if label and field:

                        response = get_lead_details(messages=extraction_messages, fields=[field],
                                                    error_dict=f"Error occurred: {label} for {field}").message_to_user
                        LeadMessageHistoryProxy.save_message(contact_number, "assistant", response, session_id)
                        send_whatsapp_message(contact_number, response)
                    else:
                        err_msg = (
                            f"Sorry, something went wrong while creating the lead in the CRM."
                            f"{' (Details: ' + str(json) + ')' if json else ''}"
                        )
                        LeadMessageHistoryProxy.save_message(contact_number, "assistant", err_msg, session_id)
                        send_whatsapp_message(contact_number, err_msg)

            except Exception as e:
                print(f"CRM create_lead API error: {e}")
                err_msg = f"Unexpected error occurred while adding lead: {e}"
                LeadMessageHistoryProxy.save_message(contact_number, "assistant", err_msg, session_id)
                send_whatsapp_message(contact_number, err_msg)
    else:

        print("Current fields", current_field)
        response = get_lead_details(messages=extraction_messages, fields=remaining_fields, error_dict = error_string).message_to_user
        print("Response", response)
        if response:
            LeadMessageHistoryProxy.save_message(contact_number, "assistant", response, session_id)
            send_whatsapp_message(contact_number, response)
        else:
            print("Error in creating response")

    return



def normalize_nationality(user_input):
    """
    Normalize a user-provided nationality/country input to a standard country name.
    Priority:
    1. Exact match (pycountry)
    2. Fuzzy match (pycountry + rapidfuzz)
    3. country_converter (coco)
    Returns None if no match.
    """
    if not user_input or not user_input.strip():
        return None

    ALLOWED_NATIONALITIES = [country.name for country in pycountry.countries]
    cleaned_input = user_input.strip()

    # 1. Exact match (case-insensitive)
    for country in ALLOWED_NATIONALITIES:
        if cleaned_input.lower() == country.lower():
            return country

    # 2. Fuzzy match
    match, score = process.extractOne(cleaned_input, ALLOWED_NATIONALITIES, scorer=fuzz.ratio)
    if score > 80:
        return match

    # 3. Use country_converter
    country = coco.convert(names=cleaned_input, to='name_short', not_found=None)
    if country and isinstance(country, str) and country != 'not found':
        return country

    return None


def serialize_lead_data(lead_dict):
    """
    Recursively converts datetime/date fields to ISO string in the lead dictionary.
    """
    from datetime import date, datetime
    for k, v in lead_dict.items():
        if isinstance(v, (datetime, date)):
            lead_dict[k] = v.isoformat()
    return lead_dict


def is_valid_phone(number):
    """
    Validates phone numbers in international E.164 format or as a general global number.
    Accepts formats like +12345678900, 00441234567890, or just digits with 10-15 numbers.
    """
    # Remove spaces and dashes for validation
    num = number.strip().replace(" ", "").replace("-", "")
    # Accepts +, 00, or just digits, 10 to 15 digits total
    pattern = re.compile(r'^(?:\+|00)?\d{10,15}$')
    return bool(pattern.match(num))
