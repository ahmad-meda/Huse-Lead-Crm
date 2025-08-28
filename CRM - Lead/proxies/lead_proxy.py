from typing import List, Optional, Tuple
from services.lead_service import LeadService

class LeadProxy:
    
    @staticmethod
    def to_get_or_create_draft(agent_id: str, **member_data) -> Tuple[int, bool, List[str]]:
        """
        Proxy function to get or create a draft member.
        
        Args:
            agent_id (str): The ID of the agent for whom to get or create a draft
            db (Session): Database session to use
            **member_data: Additional member data to include when creating a new draft
        
        Returns:
            Tuple[int, bool, List[str]]: (row_id, draft_existed, null_fields)
        """
        from app import db
        return LeadService.get_or_create_draft(agent_id=agent_id, db=db)


    @staticmethod
    def to_update_draft(draft_id: int, extracted_data) -> bool:
        """
        Proxy function to update an existing draft with extracted data.
        
        Args:
            draft_id: The ID of the draft to update
            extracted_data: Pydantic model containing the extracted lead data
            db (Session): Database session to use
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        from app import db
        return LeadService.update_draft(draft_id=draft_id, extracted_data=extracted_data, db=db)


    @staticmethod
    def to_complete_draft(draft_id: int) -> bool:
        """
        Proxy function to mark a draft as complete.
        
        Args:
            draft_id: The ID of the draft to mark as complete
            db (Session): Database session to use
        
        Returns:
            bool: True if status update was successful, False otherwise
        """
        from app import db
        return LeadService.complete_draft(draft_id=draft_id, db=db)


    @staticmethod
    def to_get_draft_by_id(draft_id: int):
        """
        Proxy function to get draft details by ID.
        
        Args:
            draft_id: The ID of the draft to retrieve
            db (Session): Database session to use
        
        Returns:
            dict or None: Dictionary with non-null field values or None if not found
        """
        from app import db
        return LeadService.get_draft_by_id(draft_id=draft_id, db=db)


    @staticmethod
    def to_clear_draft_fields(draft_id: int) -> bool:
        """
        Proxy function to clear all fields for a given draft ID except the ID field.
        
        Args:
            draft_id: The ID of the draft to clear
            db (Session): Database session to use
        
        Returns:
            bool: True if successful, False otherwise
        """
        from app import db
        return LeadService.clear_draft_fields(draft_id=draft_id, db=db)
    
    @staticmethod
    def to_get_employee_database_id_by_contact(contact_number: str) -> int:
        """
        Proxy function to get employee database ID by contact number.
        """
        from app import db
        return LeadService.get_employee_database_id_by_contact(contact_number=contact_number, db_session=db)
    
    @staticmethod
    def to_get_complete_by_id(complete_id: int):
        """
        Proxy function to get lead details by ID regardless of status.
        
        Args:
            lead_id: The ID of the lead to retrieve
        
        Returns:
            dict or None: Dictionary with non-null field values or None if not found
        """
        from app import db
        return LeadService.get_complete_by_id(complete_id=complete_id, db=db)
    
    @staticmethod
    def to_get_member_by_phone(phone_number: str, agent_id: str):
        """
        Proxy function to get member by phone number.
        """
        from app import db
        return LeadService.get_member_by_phone(session=db, phone_number=phone_number, agent_id=agent_id)
    
    @staticmethod
    def to_get_member_by_email(email_address: str, agent_id: str):
        """
        Proxy function to get member by email address.
        """
        from app import db
        return LeadService.get_member_by_email(session=db, email_address=email_address, agent_id=agent_id)
    
    @staticmethod   
    def to_get_members_by_name(name: str, agent_id: str):
        """
        Proxy function to get members by name.
        """
        from app import db
        return LeadService.get_members_by_name(session=db, name=name, agent_id=agent_id)

    @staticmethod
    def to_update_lead_status(member_id: int, new_lead_status: str):
        """
        Proxy function to update lead status.
        """
        from app import db
        return LeadService.update_lead_status(session=db, member_id=member_id, new_lead_status=new_lead_status)
    
    @staticmethod
    def to_update_member_crm_backend_id(member_id: int, crm_backend_id: str):
        """
        Proxy function to update member CRM backend ID.
        """
        from app import db
        return LeadService.update_member_crm_backend_id(db_session=db, member_id=member_id, crm_backend_id=crm_backend_id)
    
    @staticmethod
    def to_update_conversion_status(member_id: int, conversion_status: str):
        """
        Proxy function to update conversion status.
        """
        from app import db
        return LeadService.update_conversion_status(session=db, member_id=member_id, conversion_status=conversion_status)
    
    @staticmethod
    def to_get_member_id_by_phone(phone_number: str):
        """
        Proxy function to get member ID by phone number.
        """
        from app import db
        return LeadService.get_member_id_by_phone(session=db, phone_number=phone_number)
    
    @staticmethod
    def to_get_active_approvers():
        """
        Proxy function to get active employees.
        """
        from app import db
        return LeadService.get_active_approvers(session=db)
    
    @staticmethod
    def to_update_member_approval_status(member_id: int, approval_status: str):
        """
        Proxy function to update approval status.
        """
        from app import db
        return LeadService.update_member_approval_status(session=db, member_id=member_id, new_approval_status=approval_status)
    
    @staticmethod
    def to_check_conversion_status_filled(member_id: int):
        """
        Proxy function to check if conversion status is filled.
        """
        from app import db
        return LeadService.check_conversion_status_filled(session=db, member_id=member_id)
    
    @staticmethod
    def to_get_member_approval_status(member_id: int):
        """
        Proxy function to get member approval status.
        """
        from app import db
        return LeadService.get_member_approval_status(session=db, member_id=member_id)
    
    @staticmethod
    def to_get_lead_by_id(lead_id: int):
        """
        Proxy function to get lead by ID.
        """
        from app import db
        return LeadService.get_lead_by_id(db, lead_id)
    
    @staticmethod
    def _get_crm_token_by_employee_database_id(employee_database_id: int):
        """
        Proxy function to get CRM token by employee database ID.
        """
        from app import db
        return LeadService._get_crm_token_by_employee_database_id(db, employee_database_id)

    @staticmethod
    def get_employee_name_by_crm_token(crm_token: str):
        from app import db
        return LeadService.get_employee_name_by_crm_token(crm_token=crm_token, db=db)
    
    @staticmethod
    def add_lead(full_legal_name: Optional[str] = None,
                 preferred_nickname: Optional[str] = None,
                 date_of_birth: Optional[str] = None,
                 nationality: Optional[str] = None,
                 phone_number: Optional[str] = None,
                 email_address: Optional[str] = None,
                 suggested_membership_tier: Optional[str] = None,
                 residential_address: Optional[str] = None,
                 passport_number: Optional[str] = None,
                 id_number: Optional[str] = None,
                 occupation: Optional[str] = None,
                 job_title: Optional[str] = None, 
                 linkedin_or_website: Optional[str] = None,
                 education_background: Optional[str] = None,
                 notable_affiliations: Optional[str] = None,
                 lead_comments: Optional[str] = None,
                 conversion_status: Optional[str] = None,
                 approval_status: Optional[str] = None,
                 lead_status: Optional[str] = None,
                 company: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 crm_backend_id: Optional[str] = None,
                 status : Optional[str] = None,):
        """
        Proxy function to add a lead.
        """
        from app import db
        return LeadService.add_lead(db=db, full_legal_name=full_legal_name, 
                                    preferred_nickname=preferred_nickname, 
                                    date_of_birth=date_of_birth, 
                                    nationality=nationality, 
                                    phone_number=phone_number, 
                                    email_address=email_address, 
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
                                    conversion_status=conversion_status, 
                                    approval_status=approval_status, 
                                    lead_status=lead_status, 
                                    company=company, 
                                    agent_id=agent_id, 
                                    crm_backend_id=crm_backend_id, 
                                    status=status)
    

    @staticmethod
    def get_employee_by_name(name: str):
        from app import db
        return LeadService.get_employee_by_name(db=db, name=name)