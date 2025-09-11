import json
from proxies.lead_proxy import LeadProxy


def crm_to_huse(name: str, phone: str, email: str, suggested_membership_tier: str, company: str, lead_status: str,
                preferred_nickname=None, date_of_birth=None, nationality=None, residential_address=None, passport_number=None, id_number=None,
                occupation=None, job_title=None, linkedin_or_website=None, education_background=None, notable_affiliations=None, 
                lead_comments=None, approval_status=None, crm_backend_id=None, status=None):
    try:
        # Validate compulsory fields
        compulsory_fields = {
            'name': name,
            'phone': phone,
            'email': email,
            'suggested_membership_tier': suggested_membership_tier,
            'company': company,
            'lead_status': lead_status
        }
        
        missing_fields = []
        for field_name, field_value in compulsory_fields.items():
            if field_value is None or (isinstance(field_value, str) and field_value.strip() == ""):
                missing_fields.append(field_name)
        
        if missing_fields:
            raise ValueError(f"Missing compulsory fields: {', '.join(missing_fields)}. All compulsory fields must be provided and cannot be empty.")
        
        # Handle both string and dict inputs

        company_id = EmployeeProxy.get_company_by_name_only("HUSE System")
        print("company_id", company_id)
        
        group_id = EmployeeProxy.get_group_id_by_name("HUSE Group Internal")
        print("group_id", group_id)
        
        sales_employee, error_dict = EmployeeProxy.get_employee_record_by_name("System", company_id, group_id)
        agent_id = sales_employee.id
        
        print("sales_employee", sales_employee)

        # print all the fields
        print(f"full_legal_name: {name}")
        print(f"preferred_nickname: {preferred_nickname}")
        print(f"date_of_birth: {date_of_birth}")
        print(f"nationality: {nationality}")
        print(f"phone_number: {phone}")
        print(f"email_address: {email}")
        print(f"suggested_membership_tier: {suggested_membership_tier}")
        print(f"residential_address: {residential_address}")
        print(f"passport_number: {passport_number}")
        print(f"id_number: {id_number}")
        print(f"occupation: {occupation}")
        print(f"job_title: {job_title}")
        print(f"linkedin_or_website: {linkedin_or_website}")
        print(f"education_background: {education_background}")
        print(f"notable_affiliations: {notable_affiliations}")
        print(f"lead_comments: {lead_comments}")
        print(f"approval_status: {approval_status}")
        print(f"lead_status: {lead_status}")
        print(f"company: {company}")
        print(f"agent_id: {agent_id}")
        print(f"crm_backend_id: {crm_backend_id}")
        print(f"status: {status}")

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

