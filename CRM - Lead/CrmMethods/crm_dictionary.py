from datetime import datetime

def build_crm_payload(lead_details, employee_name):
    full_name = lead_details.get('full_legal_name', '')
    name_parts = full_name.split() if full_name else []
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    # Get current date for application date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Format email data
    email = lead_details.get('email_address', '')
    email_data = []
    if email:
        email_data = [{
            "emailAddress": email,
            "primary": True,
            "optOut": False,
            "invalid": False,
            "lower": email.lower()
        }]
    
    # Format phone data
    phone = lead_details.get('phone_number', '')
    phone_data = []
    if phone:
        phone_with_prefix = f"+{phone}" if not phone.startswith('+') else phone
        phone_data = [{
            "phoneNumber": phone_with_prefix,
            "primary": True,
            "type": "Mobile",
            "optOut": False,
            "invalid": False
        }]


    crm_data = {
        "status": "New",
        "cApplicationDate": current_date,
        "cMembershipCategory": lead_details.get('suggested_membership_tier', ''),
        "cNationality": lead_details.get('nationality', ''),
        "cPaymentsMembershipCategory": lead_details.get('suggested_membership_tier', ''),
        "firstName": first_name,
        "lastName": last_name,
        "name": full_name,
        "cPreferredName": lead_details.get('preferred_nickname', ''),
        "cDateOfBirth": lead_details.get('date_of_birth', ''),
        "cIdNumber": lead_details.get('id_number', ''),
        "emailAddressData": email_data,
        "emailAddress": email,
        "phoneNumberData": phone_data,
        "phoneNumber": phone_with_prefix if phone else phone,
        "cFullName": full_name,
        "cLeadStatus": lead_details.get('lead_status', ''),
        "cJobTitle": lead_details.get('job_title', ''),
        "cEmailAddress": email,
        "cPaMobileNumber": phone_with_prefix if phone else phone,
        "cStreetAddressStreet": lead_details.get('residential_address', ''),
        "cApplicantsName": full_name,
        "cCompany": lead_details.get('company', ''),
        "createdByName": employee_name,
    }
    
    crm_data = {k: v for k, v in crm_data.items() if v not in ('', None)}
    return crm_data
