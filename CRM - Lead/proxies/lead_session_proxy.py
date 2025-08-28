from services.lead_session_service import LeadSessionService

class LeadSessionProxy:
    # Create one instance to use everywhere
    _service = LeadSessionService()
    
    @classmethod
    def clear_messages(cls, contact_number):
        """Clear all messages for a given contact number"""
        return cls._service.clear_messages(contact_number)
    
    @classmethod
    def add_message(cls, contact_number, message):
        """Add a message to the contact's history"""
        return cls._service.add_message(contact_number, message)    

    @classmethod
    def get_messages(cls, contact_number):
        """Get all messages for a given contact number"""
        return cls._service.get_messages(contact_number)
    
    @classmethod
    def clear_messages(cls, contact_number):
        """Clear all messages for a given contact number"""
        return cls._service.clear_messages(contact_number)