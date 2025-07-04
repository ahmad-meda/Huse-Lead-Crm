class AgentStates:
    def __init__(self):
        self.main_fields = [
            "full_legal_name",
            "preferred_nickname", 
            "phone_number",
            "email_address",
            "lead_status",
        ]
        
        self.secondary_fields = [
            "date_of_birth",
            "nationality",    
            "suggested_membership_tier",
            "residential_address",
            "passport_number",
            "id_number",
            "occupation",
            "job_title",
            "notable_affiliations",
        ]

        self.optional_job_fields = []
        
        self.optional_education_fields = [
            "education_background",
            "lead_comments",
            "linkedin_or_website",
        ]

# Create a single instance to use throughout your application
agent_states = AgentStates()