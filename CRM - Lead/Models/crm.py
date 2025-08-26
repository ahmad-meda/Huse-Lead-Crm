from dotenv import load_dotenv
import os

load_dotenv()


class CrmData:

    def post_crm(lead_details):
        """
        Post the lead details to the CRM
        """
        print(f"Debug - Lead details: {lead_details}")
        crm_data = {
                "full_legal_name": lead_details.get('full_legal_name', ''),
                "preferred_nickname": lead_details.get('preferred_nickname', ''),
                "date_of_birth": lead_details.get('date_of_birth', ''),
                "nationality": lead_details.get('nationality', ''),
                "phone_number": lead_details.get('phone_number', ''),
                "email_address": lead_details.get('email_address', ''),
                "suggested_membership_tier": lead_details.get('suggested_membership_tier', ''),
                "residential_address": lead_details.get('residential_address', ''),
                "passport_number": lead_details.get('passport_number', ''),
                "id_number": lead_details.get('id_number', ''),
                "occupation": lead_details.get('occupation', ''),
                "job_title": lead_details.get('job_title', ''),
                "linkedin_or_website": lead_details.get('linkedin_or_website', ''),
                "education_background": lead_details.get('education_background', ''),
                "notable_affiliations": lead_details.get('notable_affiliations', ''),
                "status": lead_details.get('status', ''),
                "agent_id": lead_details.get('agent_id', ''),
                "lead_status": lead_details.get('lead_status', ''),
                "lead_comments": lead_details.get('lead_comments', '')
            }
        return crm_data