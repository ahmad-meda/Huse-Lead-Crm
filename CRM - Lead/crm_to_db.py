import json
from proxies.lead_proxy import LeadProxy

# Add details from crm object to db

crm_object = {'message': 'Lead created in CRM successfully', 'data': {'id': '68aff76b5c13065b8', 'name': 'Alexander Benjamin Rodriguez-Chen', 'deleted': False, 'firstName': 'Alexander', 'lastName': 'Benjamin Rodriguez-Chen', 'status': 'New', 'emailAddress': 'alex.rodriguez.chen@techcorp.com', 'phoneNumber': '+15550123', 'doNotCall': False, 'createdAt': '2025-08-28 06:30:03', 'modifiedAt': '2025-08-28 06:30:03', 'targetListIsOptedOut': False, 'cPreferredName': 'Alex', 'cApplicationDate': '2025-08-28', 'cGender': 'Male', 'cMembershipCategory': 'The Rufescent Business', 'cNationality': 'American Samoa', 'cDateOfBirth': '1985-03-15', 'cMaritalStatus': 'Single', 'cIdType': 'Emirates ID', 'cIdNumber': 'SSN-987-65-4321', 'cFullName': 'Alexander Benjamin Rodriguez-Chen', 'cJobTitle': 'Chief Technology Officer', 'cCompany': 'TechCorp Innovations', 'cEmailAddress': 'alex.rodriguez.chen@techcorp.com', 'cPaMobileNumber': '+1-555-0123', 'cPaymentsMembershipCategory': 'The Rufescent Business', 'cMembershipAccountSettlementMethod': 'Time of consumption', 'cApplicantsName': 'Alexander Benjamin Rodriguez-Chen', 'cSignature': False, 'cLeadStatus': 'Hot', 'cWhichAspectsAreMostValuableToYou': [], 'cIWishToSettleMyMembershipAccountBy': [], 'cApprovalStatus': 'pending', 'cSpouseInformation': False, 'cIsPaInformation': False, 'cCPaymentMethod': 'G-Pay, Apple Pay, Card', 'cIsformsubmitted': False, 'emailAddressIsOptedOut': False, 'emailAddressIsInvalid': False, 'phoneNumberIsOptedOut': False, 'phoneNumberIsInvalid': False, 'streamUpdatedAt': '2025-08-28 06:30:03', 'emailAddressData': [{'emailAddress': 'alex.rodriguez.chen@techcorp.com', 'lower': 'alex.rodriguez.chen@techcorp.com', 'primary': True, 'optOut': False, 'invalid': False}], 'phoneNumberData': [{'phoneNumber': '+15550123', 'type': 'Mobile', 'primary': True, 'optOut': False, 'invalid': False}], 'createdById': '684882bb7d1285cb4', 'createdByName': 'Ahmad Meda', 'modifiedByName': None, 'assignedUserName': None, 'teamsIds': [], 'teamsNames': {}, 'campaignName': None, 'createdAccountName': None, 'createdContactName': None, 'createdOpportunityName': None, 'isFollowed': False, 'followersIds': [], 'followersNames': {}, 'profile_image': None, 'document_attachments': None, 'signature': None}, 'lead_form_url': 'https://dev-rufescent-experience.rufescent.com?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsZWFkX2lkIjoiNjhhZmY3NmI1YzEzMDY1YjgifQ.qUWkWY3JSON8yte-LlSRK6nB-HDa386y0waTmWKCE-I', 'aml_result_url': 'https://aml-pt2u.vercel.app/result?crm_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsZWFkX2lkIjoiNjhhZmY3NmI1YzEzMDY1YjgifQ.qUWkWY3JSON8yte-LlSRK6nB-HDa386y0waTmWKCE-I', 'failure': False}

def crm_to_huse(crm_object):
    """
    Convert CRM object to Huse database format and add lead.
    
    Args:
        crm_object: JSON string or dict containing CRM lead data
    """
    try:
        # Handle both string and dict inputs
        if isinstance(crm_object, str):
            crm_object = json.loads(crm_object)
            print("json version of crm_object", crm_object)
        
        print("Processing CRM object:", crm_object)
        
        # Get details from crm object
        data = crm_object["data"]
        
        # Extract required fields with fallbacks
        name = data.get("name") or data.get("cFullName")
        preferred_nickname = data.get("cPreferredName") 
        email = data.get("emailAddress") or data.get("cEmailAddress")
        phone = data.get("phoneNumber") or data.get("cPaMobileNumber")
        date_of_birth = data.get("cDateOfBirth")
        nationality = data.get("cNationality")
        suggested_membership_tier = data.get("cMembershipCategory")
        
        # Handle residential address (not in sample data, so provide fallback)
        residential_address = data.get("cResidentialAddress")
        
        # Extract optional fields (only using fields that actually exist in the CRM object)
        company = data.get("cCompany")
        lead_status = data.get("cLeadStatus") 
        approval_status = data.get("cApprovalStatus")
        conversion_status = None  # Field doesn't exist in CRM
        passport_number = None  # Field doesn't exist in CRM
        id_number = data.get("cIdNumber")
        occupation = data.get("cJobTitle")
        job_title = data.get("cJobTitle")
        linkedin_or_website = None  # Field doesn't exist in CRM
        education_background = None  # Field doesn't exist in CRM
        notable_affiliations = None  # Field doesn't exist in CRM
        lead_comments = None  # Field doesn't exist in CRM
        agent_id = None # this fields refres the crm id of the agent who created the lead wheres to save in db we need the db id of the agent who created the lead
        crm_backend_id = data.get("id")
        status = data.get("status")
        
        # Add lead to database with all fields
        result = LeadProxy.add_lead(
            full_legal_name=name,
            preferred_nickname=preferred_nickname,
            date_of_birth=date_of_birth,
            nationality=nationality,
            phone_number=phone,
            email_address=email,
            suggested_membership_tier=suggested_membership_tier,
            residential_address=residential_address,
            passport_number=passport_number,
            id_number=id_number,
            occupation=occupation,
            job_title=job_title,
            linkedin_or_website=linkedin_or_website,
            education_background=education_background,
            notable_affiliations=notable_affiliations,
            lead_comments=lead_comments,
            approval_status=approval_status,
            lead_status=lead_status,
            company=company,
            agent_id=agent_id,
            crm_backend_id=crm_backend_id,
            status=status
        )
        
        if result == True:
            # Create detailed response similar to CRM format
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Build detailed response with only the fields that were actually added to the database
            detailed_response = {
                'message': 'Lead added to Huse database successfully',
                'data': {
                    'id': crm_backend_id,  # CRM ID
                    'full_legal_name': name,
                    'preferred_nickname': preferred_nickname,
                    'date_of_birth': date_of_birth,
                    'nationality': nationality,
                    'phone_number': phone,
                    'email_address': email,
                    'suggested_membership_tier': suggested_membership_tier,
                    'residential_address': residential_address,
                    'passport_number': passport_number,
                    'id_number': id_number,
                    'occupation': occupation,
                    'job_title': job_title,
                    'linkedin_or_website': linkedin_or_website,
                    'education_background': education_background,
                    'notable_affiliations': notable_affiliations,
                    'lead_comments': lead_comments,
                    'approval_status': approval_status,
                    'lead_status': lead_status,
                    'company': company,
                    'agent_id': agent_id,
                    'crm_backend_id': crm_backend_id,
                    'status': status
                },
                'failure': False
            }
            
            print(f"Successfully added lead: {name}")
            return detailed_response
        else:
            # Handle failure case
            error_message = str(result) if result else "Unknown database error occurred"
            failure_response = {
                'message': 'Failed to add lead to Huse database',
                'error': error_message,
                'data': {
                    'id': crm_backend_id,
                    'full_legal_name': name,
                    'email_address': email,
                    'phone_number': phone
                },
                'failure': True
            }
            
            print(f"Failed to add lead {name}: {error_message}")
            return failure_response
        
    except Exception as e:
        print(f"Error processing CRM object: {e}")
        raise






#test the function
# print(crm_to_huse(crm_object))

