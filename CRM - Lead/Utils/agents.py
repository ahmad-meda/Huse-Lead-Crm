from Utils.ai_client import client
from pydantic import BaseModel, Field
from typing import List, Optional
from Utils.formats import LeadAgent, LeadData, SkippedDetails, SkipAllOptional, UserWantsToRefreshDraft, ExtractedDataForLeadStateAllocation, LeadStateAllocationAgent, ChooseName, AgentUpdateLead, UpdateLead

# Model to Chat and ask the user for
def get_lead_details(messages, fields: list):
        system_message = [
            {
                "role": "system",
                "content": (
                    f"""

                    Ask the user these fields in one go: {fields}in a polite conversational way.
                    Always refer to the lead in the third person, even if the sales agent uses first-person language. Do not assume the details being shared are about the sales agent themselves. ."""
                )
            }
        ] + messages

        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=system_message,
            response_format=LeadAgent,
        )
        return completion.choices[0].message.parsed

# Function to extract lead details
def extract_data(messages, list_of_fields: dict):
    extraction_messages = [
        {
            "role": "system",
            "content": (
                f"""Extract ALL lead information from the ENTIRE conversation history. 

                Here is the lead record: {list_of_fields}
                From this conversation, extract the fields that are empty and the fields that are provided by the user.
                    
            IMPORTANT: Only extract NEW information that the user is providing in their current message.
            
            IMPORTANT RULES:
            - Include ALL details mentioned at ANY point in the conversation
            - Use exact values provided by the user
            - For missing information, use empty strings or None
            - Be thorough - check every message for lead details
            - Only extract fields that exist in the LeadData schema
            - Keep passport_number and id_number as strings when provided
            - Ensure phone numbers and emails are captured exactly as provided
            
            FIELDS TO EXTRACT:
            - full_legal_name, preferred_nickname, phone_number, email_address (main fields)
            - date_of_birth, nationality, suggested_membership_tier, residential_address, passport_number, id_number (secondary main fields)
            - occupation, job_title, linkedin_or_website (optional job fields)
            - education_background, notable_affiliations (optional education fields)
            
            FIELD HANDLING:
            - full_legal_name: Complete legal name as provided
            - preferred_nickname: How they prefer to be called/addressed
            - phone_number: Extract with country code if provided
            - email_address: Complete email address
            - date_of_birth: Date in postgres format mentioned (YYYY-MM-DD)
            - nationality: Country of citizenship/nationality
            - suggested_membership_tier: Any membership level mentioned
            - residential_address: Complete home/residential address
            - passport_number: Passport number as string
            - id_number: National ID/identification number as string
            - occupation: Current field of work or specialization
            - job_title: Official job title or designation
            - linkedin_or_website: LinkedIn profile URL or personal website link
            - education_background: Degrees, certifications, schools attended
            - notable_affiliations: Any associations, organizations, or prestigious groups the person is affiliated with
            - lead_status: Status of the lead
            - lead_comments: Comments about the lead
            - company: Company name of the lead
            """
            )
        }
    ] + messages
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=extraction_messages,
        response_format=LeadData,
    )
    return completion.choices[0].message.parsed

def skipped_lead_details(messages, fields: list):
            skipped_messages = [
                {
                    "role": "system",
                    "content": (
                        f"""You are analyzing a conversation to identify which specific fields from this list the user EXPLICITLY wants to skip: {fields}

                            IMPORTANT: Only mark fields as skipped if the user has CLEARLY and EXPLICITLY indicated they want to skip them.

                            Mark a field as skipped ONLY if the user:
                            - Explicitly says "skip [field_name]" or "I don't want to provide [field_name]"
                            - Says "no" when directly asked about a specific field
                            - Clearly states they don't have or don't want to share that specific information
                            - Uses phrases like "skip that one", "not that", "don't need that" when referring to specific fields

                            DO NOT mark fields as skipped if the user:
                            - Says general words like "continue", "next", "proceed", "go ahead"
                            - Shows willingness to provide information
                            - Asks questions about what's needed
                            - Simply hasn't mentioned the field yet
                            - Says "ok" or "sure" or shows agreement
                            - Wants to move forward with the process

                            Current fields to analyze: {fields}

                            Return ONLY the fields that the user has EXPLICITLY requested to skip. If no fields were explicitly marked for skipping, return an empty list.
                            """
                            )
                }
            ] + messages

            completion = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=skipped_messages,
                response_format=SkippedDetails,
            )
            return completion.choices[0].message.parsed

def check_skip_all_optional(messages):
        """
        Check if user wants to skip ALL optional fields (both job and education)
        """
        class SkipAllOptional(BaseModel):
            skip_all_optional: bool = False

        skip_all_messages = [
            {
                "role": "system", 
                "content": (
                    """Look at the recent user messages and determine if the user wants to skip ALL remaining optional fields (both job AND education fields).

                        IMPORTANT: This should ONLY be True if the user wants to skip EVERYTHING and finish the process completely.

                        Set skip_all_optional to True ONLY if the user explicitly says:
                        - "skip all", "skip everything", "skip all optional fields", "skip the rest"
                        - "I'm done", "that's all", "finish now", "complete it", "I don't want to provide any more information"
                        - "skip all remaining fields", "skip everything else"
                        - Clear indication they want to finish the entire process without providing ANY more optional information

                        Set skip_all_optional to False if the user:
                        - Only mentions skipping specific fields (like "skip these three", "skip job details", "skip occupation")
                        - Only refers to the current set of fields being asked about
                        - Says "skip these" or "skip this" (referring to current fields only)
                        - Shows they might be willing to provide other types of optional information
                        - Doesn't clearly indicate they want to skip EVERYTHING remaining

                        Remember: Skipping the current set of fields (like job fields) does NOT mean they want to skip ALL optional fields (like education fields too).
                    """
                )
            }
        ] + messages

        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=skip_all_messages,
            response_format=SkipAllOptional,
        )
        return completion.choices[0].message.parsed.skip_all_optional


def if_user_wants_to_refresh_draft(messages):
        """
        Check if the user wants to refresh the draft
        """

        refresh_messages = [
            {
                "role": "system",
                "content": (
                    """Look at the recent user messages and determine if the user wants to refresh the draft.
                    
                    Set refresh_draft to True if the user:
                    - Says "refresh draft", "start over", "clear draft", "new draft"
                    - Indicates they want to discard current information and start fresh
                    
                    Set refresh_draft to False if the user:
                    - Wants to continue with existing draft
                    - Is providing additional information without asking for a reset
                    """
                )
            }
        ] + messages

        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=refresh_messages,
            response_format=UserWantsToRefreshDraft,
        )
        return completion.choices[0].message.parsed.refresh_draft

def extracted_data_for_lead_state_allocation(messages):
       """
       Extract the data for lead state allocation from the user's message.
       """
       extracted_data_for_lead_state_allocation_messages = [
            {
                "role": "system",
                "content": (
                    """Extract the data for lead state allocation from the user's message.Change the boolean values to true or false based on the user's message.
                    and then set the chosen_conversion_status to the conversion status the user has chosen."""
                )
            }
       ] + messages

       completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=extracted_data_for_lead_state_allocation_messages,
            response_format=ExtractedDataForLeadStateAllocation,
       )
       return completion.choices[0].message.parsed

def lead_state_allocation_agent(messages):
       """
       Allocate the lead state based on the user's message.
       """
       lead_state_allocation_agent_messages = [
            {
                "role": "system",
                "content": (
                        """Your task is to chat with the user until he gives a clear decision. Make sure the conversation goes smoothly based on the chat history. Be understanding like a human friend
                    """
                )
            }
       ] + messages

       completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=lead_state_allocation_agent_messages,
            response_format=LeadStateAllocationAgent,
       )
       return completion.choices[0].message.parsed

def choose_name_from_multiple_leads(messages: list, members: list):

        choose_name_message = [
            {
                "role": "system",
                "content": (
                    f"""You are an assistant helping the user choose a specific lead from multiple leads with similar names. You will be provided a chat history and need to extract which lead the user wants to select.
                
                Available leads: {members}
                
                If the user has clearly chosen a specific lead, you will set the has_the_name_been_chosen field to true.
                If the user has not chosen a specific lead yet, you will set the has_the_name_been_chosen field to false.
                
                If the user has chosen a lead, you will set the name_chosen field to the EXACT name from the member list above.
                If the user has not chosen a lead, you will set the name_chosen field to empty string.
                
                Chat with the user naturally based on the provided chat history. Your goal is to help them identify which specific lead they want to update.
                
                If a lead is chosen or if the user wants to exit the chat, you will set the has_the_name_been_chosen field to true and provide a confirmation message.
                If the user has not chosen a specific lead, you will set the has_the_name_been_chosen field to false and provide a message asking them to clarify which lead they mean by providing more details like email address or being more specific about the name.
                """
                )
            }
        ] + messages

        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=choose_name_message,
            response_format=ChooseName,
        )
        return completion.choices[0].message.parsed

def get_lead_update_details(messages, fields: list):
        """
        Get the lead updated details from the user
        """
        system_message = [
            {
                "role": "system",
                "content": (
                    f"""You are a friendly HR assistant helping a sales agent update a lead's status in the CRM system.

                        To update a lead, you need to collect:
                        1. ONE way to identify the lead: phone number, email address, OR full name
                        2. The new lead status they want to update to

                        Current fields needed: {fields}

                        Instructions:
                        - Be conversational and friendly
                        - Explain that you need to identify which lead to update and what the new status should be
                        - Ask for the lead identification info (phone/email/name) and new lead status together in one message
                        - Make it clear that they only need to provide ONE of the identification methods (phone OR email OR name)
                        - If they've already provided some information, only ask for what's still missing
                        - Be helpful and guide them through the process

                        Example: "Hi! I can help you update a lead's status. To do this, I'll need to identify which lead you want to update and what the new status should be. Please provide either the lead's phone number, email address, or full name, along with the new lead status you'd like to set."
                    """
                )
            }
        ] + messages

        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=system_message,
            response_format=AgentUpdateLead,
        )
        return completion.choices[0].message.parsed

def extract_data_to_update(messages, fields: list):
    """
    Extract the lead updated details from the conversation
    """
    extraction_messages = [
        {
            "role": "system",
            "content": (
                f"""Extract the following information from the conversation history: {fields}
                """
            )
        }
    ] + messages

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=extraction_messages,
        response_format=UpdateLead,
    )
    return completion.choices[0].message.parsed
