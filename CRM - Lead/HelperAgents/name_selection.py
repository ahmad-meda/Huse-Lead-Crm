from Utils.formats import ChooseName
from Utils.ai_client import client



def choose_name(members: list, messages: list):

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
                model="gemini-2.0-flash",
                messages=choose_name_message,
                response_format=ChooseName,
            )
            return completion.choices[0].message.parsed
    
    while True:
        response = choose_name_from_multiple_leads(messages, members)
        if response.has_the_name_been_chosen:
            print(response.has_the_name_been_chosen)
            print(response.message_to_user)
            if response.name_chosen:
                print(f"Name chosen: {response.name_chosen}")
                messages.append({"role": "assistant", "content": f"Name chosen: {response.name_chosen}"})

            return messages, response.name_chosen
        messages.append({"role": "assistant", "content": response.message_to_user})
        print(f"Assistant: {response.message_to_user}")
        user_input = input("User: ")
        messages.append({"role": "user", "content": user_input})
        
        

