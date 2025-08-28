class UpdateLeadStates:
    def __init__(self):
        self.main_fields = [
            "full_legal_name",
            "phone_number",
            "email_address",
            "lead_status",
        ]
        

# Create a single instance to use throughout your application
update_lead_states = UpdateLeadStates()