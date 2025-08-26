from pydantic import BaseModel
from proxies.lead_proxy import LeadProxy
from create_lead_api import add_lead_in_crm
# Define a Pydantic model for the request body
class LeadRequest(BaseModel):
    full_legal_name: str
    phone_number: str
    email_address: str
    suggested_membership_tier: str
    company: str
    lead_status: str

full_name = "John Doe"
phone_number = "+9715092673826"
email_address = "john.doina@example.com"
suggested_membership_tier = "The Rufescent Business"
company = "Example Inc."
lead_status = "Hot"

print(add_lead_in_crm(contact_number="+971509565289", full_name=full_name, phone_number=phone_number, email_address=email_address, suggested_membership_tier=suggested_membership_tier, company=company, lead_status=lead_status))