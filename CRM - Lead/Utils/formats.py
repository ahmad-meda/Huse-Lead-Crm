"""
Data models for lead management system
"""
from pydantic import BaseModel
from typing import Optional, List


class LeadData(BaseModel):
    """Main lead data structure containing all member information"""
    full_legal_name: str
    preferred_nickname: str
    date_of_birth: str
    nationality: str
    phone_number: str
    email_address: str
    lead_status: str
    suggested_membership_tier: str
    residential_address: str
    passport_number: Optional[str] = None  
    id_number: Optional[str] = None        
    occupation: Optional[str] = None       
    job_title: Optional[str] = None
    linkedin_or_website: Optional[str] = None  
    education_background: Optional[str] = None
    notable_affiliations: Optional[str] = None
    lead_comments: Optional[str] = None
    company: Optional[str] = None

class LeadAgent(BaseModel):
    """Response model for agent messages to user"""
    message_to_user: str = ""

class SkippedDetails(BaseModel):
    """Model to track which fields user wants to skip"""
    fields_the_user_wants_to_skip: List[str] = []

class UserWantsToRefreshDraft(BaseModel):
    """Model to check if user wants to refresh/restart the draft"""
    refresh_draft: bool = False


class SkipAllOptional(BaseModel):
    """Model to check if user wants to skip all optional fields"""
    skip_all_optional: bool = False

class UpdateLead(BaseModel):
    """Model to update the lead details"""
    full_legal_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    lead_status: Optional[str] = None

class AgentUpdateLead(BaseModel):
    """Model to update the lead details"""
    message_to_user: str = ""
    
class ChooseName(BaseModel):
    """Model to choose a name from a list of multiple leads"""
    has_the_name_been_chosen: bool = False
    name_chosen: str = ""
    message_to_user: str = ""

class ExtractedDataForLeadStateAllocation(BaseModel):
    """Model to extract the data for lead state allocation"""
    Approve: Optional[bool] = False
    Reject: Optional[bool] = False
    Flag: Optional[bool] = False
    Waitlist: Optional[bool] = False
    chosen_conversion_status: Optional[str] = None
   
class LeadStateAllocationAgent(BaseModel):
    """Model to allocate the lead state"""
    message_to_user: str = ""