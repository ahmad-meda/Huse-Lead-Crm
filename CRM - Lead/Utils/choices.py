import pycountry

class LeadChoices:

    @staticmethod
    def get_membership_choices():
        return [
            "The Rufescent Preferred",
            "The Rufescent Business",
            "The Blue Lotus",
            "The Rufescent Associate"
        ]
    
    @staticmethod
    def get_lead_status_choices():
        return [
            "Hot",
            "Warm",
            "Cold"
        ]

    @staticmethod
    def get_country_choices():
        country_names = [country.name for country in pycountry.countries]
        return country_names
    