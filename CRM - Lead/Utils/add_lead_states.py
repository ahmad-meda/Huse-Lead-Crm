class AgentStates:
    def __init__(self):
        self.main_fields = [
            "full_legal_name",
            "phone_number",
            "email_address",
            "suggested_membership_tier",
            "company",
        ]
        
        self.secondary_fields = []

        self.optional_job_fields = []
        
        self.optional_education_fields = []

# Create a single instance to use throughout your application
agent_states = AgentStates()