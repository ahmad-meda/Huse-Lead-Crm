from sqlalchemy.orm import Session
from Files.SQLAlchemyModels import Member, Employee, Approval, SalesTeam
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from typing import Tuple, List



class LeadService:
    """Service class for managing lead/member draft operations"""

    @staticmethod
    def get_or_create_draft(
        agent_id: str,
        db: Session,
        **member_data
    ) -> Tuple[int, bool, List[str]]:
        """
        Check if a row with draft status exists for the given agent_id and return its ID,
        or create a new draft row with the given agent_id and return the new ID.
        Also return list of fields that are currently NULL.

        Args:
            agent_id (str): The ID of the agent for whom to get or create a draft
            db (Session): Database session to use
            **member_data: Additional member data to include when creating a new draft

        Returns:
            Tuple[int, bool, List[str]]: (row_id, draft_existed, null_fields)
        """
        try:
            # Convert agent_id to string to ensure type compatibility
            agent_id_str = str(agent_id)
            
            # Try to find existing draft for the specific agent
            existing_draft = db.query(Member).filter(
                Member.status == 'draft',
                Member.agent_id == agent_id_str
            ).first()

            if existing_draft:
                draft = existing_draft
                existed = True
            else:
                # Create new draft with the specified agent_id
                draft = Member(status='draft', agent_id=agent_id_str, **member_data)
                db.add(draft)
                db.commit()
                db.refresh(draft)
                existed = False

            # Identify fields that are NULL
            null_fields = [
                column.name
                for column in Member.__table__.columns
                if getattr(draft, column.name) is None
            ]

            return draft.id, existed, null_fields

        except Exception as e:
            db.rollback()
            raise e


    @staticmethod
    def update_draft(draft_id: int, extracted_data, db: Session) -> bool:
        """
        Update an existing draft with extracted data.
        
        Args:
            draft_id: The ID of the draft to update
            extracted_data: Pydantic model containing the extracted lead data
            db (Session): Database session to use
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Find the draft by ID
            draft = db.query(Member).filter(
                Member.id == draft_id,
                Member.status == 'draft'
            ).first()
            
            if not draft:
                print(f"No draft found with ID: {draft_id}")
                return False
            
            # Update fields with non-empty values from extracted data
            update_data = {}
            for field_name in extracted_data.__fields__.keys():
                value = getattr(extracted_data, field_name)
                if value is not None and value != "":
                    # Handle date conversion for date_of_birth
                    if field_name == 'date_of_birth' and isinstance(value, str):
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Invalid date format for {field_name}: {value}")
                            continue
                    update_data[field_name] = value
            
            if not update_data:
                # No new data to update
                return True
            
            # Update the draft
            for key, value in update_data.items():
                if hasattr(draft, key):
                    setattr(draft, key, value)
            
            db.commit()
            print(f"Draft {draft_id} updated successfully with fields: {list(update_data.keys())}")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Database error during draft update: {e}")
            return False


    @staticmethod
    def complete_draft(draft_id: int, db: Session) -> bool:
        """
        Update the status of a draft to 'complete' when all required information is collected.
        
        Args:
            draft_id: The ID of the draft to mark as complete
            db (Session): Database session to use
        
        Returns:
            bool: True if status update was successful, False otherwise
        """
        try:
            # Find the draft by ID
            draft = db.query(Member).filter(
                Member.id == draft_id,
                Member.status == 'draft'
            ).first()
            
            if not draft:
                print(f"No draft found with ID: {draft_id}")
                return False
            
            # Update status to complete
            draft.status = 'New'
            db.commit()
            
            print(f"Draft {draft_id} marked as complete successfully!")
            print(f"Member: {draft.full_legal_name} ({draft.email_address})")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Database error during draft completion: {e}")
            return False


    @staticmethod
    def get_draft_by_id(draft_id: int, db: Session):
        """
        Get draft details by ID - improved version
        
        Args:
            draft_id: The ID of the draft to retrieve
            db (Session): Database session to use
        
        Returns:
            dict or None: Dictionary with non-null field values or None if not found
        """
        try:
            draft = db.query(Member).filter(
                Member.id == draft_id,
                Member.status == 'draft'
            ).first()
            
            if draft:
                # Create a dictionary with only non-null field values
                result = {}
                for column in Member.__table__.columns:
                    value = getattr(draft, column.name)
                    if value is not None and value != '':
                        result[column.name] = value
                return result
            else:
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None


    @staticmethod
    def clear_draft_fields(draft_id: int, db: Session):
        """
        Clear all fields for a given draft ID except the ID field
        
        Args:
            draft_id: The ID of the draft to clear
            db (Session): Database session to use
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Find the draft
            draft = db.query(Member).filter(
                Member.id == draft_id,
                Member.status == 'draft'
            ).first()
            
            if draft:
                # Set all fields to None except id
                draft.full_legal_name = None
                draft.preferred_nickname = None
                draft.date_of_birth = None
                draft.nationality = None
                draft.phone_number = None
                draft.email_address = None
                draft.suggested_membership_tier = None
                draft.residential_address = None
                draft.passport_number = None
                draft.id_number = None
                draft.occupation = None
                draft.job_title = None
                draft.linkedin_or_website = None
                draft.education_background = None
                draft.notable_affiliations = None
                # Keep status as 'draft'
                
                # Commit the changes
                db.commit()
                print(f"Successfully cleared all fields for draft ID: {draft_id}")
                return True
            else:
                print(f"No draft found with ID: {draft_id}")
                return False
                
        except Exception as e:
            print(f"Error clearing draft fields: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_employee_database_id_by_contact(contact_number: str, db_session) -> int:
        """
        Retrieve employee's database ID by contact number.
        
        Args:
            contact_number (str): The contact number to search for
            db_session: SQLAlchemy database session
            
        Returns:
            int: The database_id of the employee if found
            
        Raises:
            ValueError: If no employee is found with the given contact number
            Exception: For any database-related errors
        """
        try:
            # Query the employee by contact number
            employee = db_session.query(Employee).filter(
                Employee.contactno == contact_number
            ).first()
            
            if employee is None:
                raise ValueError(f"No employee found with contact number: {contact_number}")
                
            return employee.database_id
            
        except Exception as e:
            # Re-raise the exception with more context
            raise Exception(f"Error retrieving employee by contact number {contact_number}: {str(e)}")
        
    @staticmethod
    def get_complete_by_id(complete_id: int, db: Session):      
        """
        Get complete member details by ID - improved version
        
        Args:
            complete_id: The ID of the complete member to retrieve
            db (Session): Database session to use
        
        Returns:
            dict or None: Dictionary with non-null field values or None if not found
        """
        try:
            complete_member = db.query(Member).filter(
                Member.id == complete_id).first()
            
            if complete_member:
                # Create a dictionary with only non-null field values
                result = {}
                for column in Member.__table__.columns:
                    value = getattr(complete_member, column.name)
                    if value is not None and value != '':
                        result[column.name] = value
                return result
            else:
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None 
        
    @staticmethod
    def get_member_by_phone(session: Session, phone_number: str, agent_id: str):
        """
        Get a member record by phone number and agent ID.
        
        Args:
            session: SQLAlchemy session object
            phone_number (str): The phone number to search for
            agent_id (str): The agent ID to match
            
        Returns:
            Member: Member object if found, None if not found
        """
        try:
            member = session.query(Member).filter(
                Member.phone_number == phone_number,
                Member.agent_id == agent_id
            ).first()
            return member
        except Exception as e:
            session.rollback()
            raise e


    @staticmethod
    def get_member_by_email(session: Session, email_address: str, agent_id: str):
        """
        Get a member record by email address and agent ID.
        
        Args:
            session: SQLAlchemy session object
            email_address (str): The email address to search for
            agent_id (str): The agent ID to match
            
        Returns:
            Member: Member object if found, None if not found
        """
        try:
            member = session.query(Member).filter(
                Member.email_address == email_address,
                Member.agent_id == agent_id
            ).first()
            return member
        except Exception as e:
            print(f"Error retrieving member by email: {e}")
            return None


    @staticmethod
    def get_members_by_name(session: Session, name: str, agent_id: str):
        """
        Get member records by name and agent ID (searches full_legal_name only).
        
        Args:
            session: SQLAlchemy session object
            name (str): The name to search for (partial matches supported)
            agent_id (str): The agent ID to match
            
        Returns:
            list: List of Member objects that match the name search and agent ID
        """
        try:
            # Search for partial matches in full_legal_name with agent_id filter
            members = session.query(Member).filter(
                Member.full_legal_name.ilike(f'%{name}%'),
                Member.agent_id == agent_id
            ).all()
            return members
        except Exception as e:
            print(f"Error retrieving members by name: {e}")
            return []

    @staticmethod
    def update_lead_status(session: Session, member_id: int, new_lead_status: str):
        """
        Update the lead_status for a specific member.
        
        Args:
            session: SQLAlchemy session object
            member_id (int): The ID of the member to update
            new_lead_status (str): The new lead status value
            
        Returns:
            bool: True if update was successful, False if member not found
            
        Raises:
            Exception: If database error occurs
        """
        try:
            # Find the member by ID
            member = session.query(Member).filter(Member.id == member_id).first()
            
            if member:
                # Update the lead_status
                member.lead_status = new_lead_status
                session.commit()
                return True
            else:
                return False
                
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def update_member_crm_backend_id(db_session, member_id: int, crm_backend_id: str) -> bool:
        """
        Update the crm_backend_id for a specific member.
        
        Args:
            db_session: SQLAlchemy database session
            member_id (int): The ID of the member to update
            crm_backend_id (str): The CRM backend ID value to set
        
        Returns:
            bool: True if update was successful, False if member not found
        
        Raises:
            Exception: If there's a database error during the update
        """
        try:
            # Find the member by ID
            member = db_session.query(Member).filter(Member.id == member_id).first()
            
            if not member:
                print(f"Member with ID {member_id} not found")
                return False
            
            # Update the crm_backend_id
            member.crm_backend_id = crm_backend_id
            
            # Commit the changes
            db_session.commit()
            
            print(f"Successfully updated crm_backend_id for member ID {member_id}")
            return True
            
        except Exception as e:
            # Rollback in case of error
            db_session.rollback()
            print(f"Error updating member: {str(e)}")
            raise e
        
    @staticmethod
    def update_conversion_status(session: Session, member_id: int, conversion_status: str) -> bool:
        """
        Update the conversion_status of a member by their ID.
        
        Args:
            session (Session): SQLAlchemy session object
            member_id (int): The ID of the member to update
            conversion_status (str): The new conversion status value
            
        Returns:
            bool: True if update was successful, False if member not found
            
        Raises:
            Exception: If there's a database error during the update
        """
        try:
            # Find the member by ID
            member = session.query(Member).filter(Member.id == member_id).first()
            
            if not member:
                print(f"Member with ID {member_id} not found")
                return False
            
            # Update the conversion_status
            member.conversion_status = conversion_status
            
            # Commit the changes
            session.commit()
            
            print(f"Successfully updated conversion_status for member {member_id} to '{conversion_status}'")
            return True
            
        except Exception as e:
            # Rollback in case of error
            session.rollback()
            print(f"Error updating conversion_status: {e}")
            raise e


    @staticmethod
    def get_member_id_by_phone(session: Session, phone_number: str):
        """
        Get a member's database ID by phone number.
        
        Args:
            session: SQLAlchemy session object
            phone_number (str): The phone number to search for
            
        Returns:
            int: Member's database ID if found, None if not found
        """
        try:
            member = session.query(Member.id).filter(
                Member.phone_number == phone_number
            ).first()
            return member.id if member else None
        except Exception as e:
            session.rollback()
            raise e
        
    @staticmethod
    def get_active_approvers(session: Session):
        active_status = 3       
        # Query join Approval and Employee where status == active_status
        results = (
            session.query(Employee.database_id, Employee.name, Employee.emailid)
            .join(Approval, Approval.user_id == Employee.database_id)
            .filter(Approval.status == active_status)
            .all()
        )
        return results
    
    @staticmethod
    def update_member_approval_status(session, member_id, new_approval_status):
        """
        Update the approval status of a member by their ID.
        
        Args:
            session: SQLAlchemy session object
            member_id (int): The ID of the member to update
            new_approval_status (str): The new approval status to set
        
        Returns:
            bool: True if update was successful, False if member not found
        
        Raises:
            Exception: If there's a database error during the update
        """
        try:
            # Query for the member by ID
            member = session.query(Member).filter(Member.id == member_id).first()
            
            if member is None:
                print(f"Member with ID {member_id} not found")
                return False
            
            # Update the approval status
            member.approval_status = new_approval_status
            
            # Commit the changes
            session.commit()
            
            print(f"Successfully updated approval status for member ID {member_id} to '{new_approval_status}'")
            return True
            
        except Exception as e:
            # Rollback in case of error
            session.rollback()
            print(f"Error updating member approval status: {str(e)}")
            raise e
        
    @staticmethod
    def check_conversion_status_filled(session, member_id):
        """
        Check if a member's conversion status has been filled with one of the valid statuses.
        
        Args:
            session: SQLAlchemy session object
            member_id (int): The ID of the member to check
        
        Returns:
            dict: Contains 'found' (bool), 'has_valid_status' (bool), 'current_status' (str or None)
        
        Raises:
            Exception: If there's a database error during the query
        """
        # Valid conversion statuses
        valid_statuses = ['approved', 'flagged', 'rejected', 'waitlisted']
        
        try:
            # Query for the member by ID
            member = session.query(Member).filter(Member.id == member_id).first()
            
            if member is None:
                print(f"Member with ID {member_id} not found")
                return {
                    'found': False,
                    'has_valid_status': False,
                    'current_status': None
                }
            
            # Check if conversion status is filled and valid
            current_status = member.conversion_status
            
            if current_status is None:
                print(f"Member ID {member_id} has no conversion status set")
                return {
                    'found': True,
                    'has_valid_status': False,
                    'current_status': None
                }
            
            # Check if the current status is one of the valid ones (case-insensitive)
            has_valid_status = current_status.lower() in valid_statuses
            
            if has_valid_status:
                print(f"Member ID {member_id} has valid conversion status: '{current_status}'")
            else:
                print(f"Member ID {member_id} has invalid conversion status: '{current_status}'")
                print(f"Valid statuses are: {', '.join(valid_statuses)}")
            
            return {
                'found': True,
                'has_valid_status': has_valid_status,
                'current_status': current_status
            }
            
        except Exception as e:
            print(f"Error checking conversion status: {str(e)}")
            raise e

    @staticmethod
    def get_member_approval_status(session, member_id):
        """
        Get the current approval status of a member by their ID.
        
        Args:
            session: SQLAlchemy session object
            member_id (int): The ID of the member to query
        
        Returns:
            str or None: The current approval status value, or None if member not found
        
        Raises:
            Exception: If there's a database error during the query
        """
        try:
            # Query for the member by ID
            member = session.query(Member).filter(Member.id == member_id).first()
            
            if member is None:
                print(f"Member with ID {member_id} not found")
                return None
            
            # Return the current approval status
            approval_status = member.approval_status
            print(f"Member ID {member_id} has approval status: '{approval_status}'")
            return approval_status
            
        except Exception as e:
            print(f"Error retrieving approval status: {str(e)}")
            raise e

    @staticmethod
    def get_lead_by_id(session, lead_id):
        """
        Get lead details by ID - improved version
        
        Args:
            lead_id: The ID of the lead to retrieve
            db (Session): Database session to use
            
        Returns:
            dict or None: Dictionary with non-null field values or None if not found
        """
        try:
            lead = session.query(Member).filter(Member.id == lead_id).first()
            
            if lead:
                # Create a dictionary with only non-null field values
                result = {}
                for column in Member.__table__.columns:
                    value = getattr(lead, column.name)
                    if value is not None and value != '':
                        result[column.name] = value
                return result
            else:
                return None
        except Exception as e:
            print(f"Error retrieving lead with ID {lead_id}: {str(e)}")
            raise e

    @staticmethod
    def _get_crm_token_by_employee_database_id(session: Session, employee_id: int) -> str:
        try:
            crm_token = session.query(SalesTeam.crm_token).filter(
                SalesTeam.employee_id == employee_id
            ).one()[0]  # `one()` returns a tuple like (crm_token,), so use [0]
            
            return crm_token

        except NoResultFound:
            return None
        
    @staticmethod
    def get_employee_name_by_crm_token(crm_token: str, db: Session):
        try:
            result = db.query(Employee.name).join(SalesTeam).filter(SalesTeam.crm_token == crm_token).one()
            return result.name
        except NoResultFound:
            return None
