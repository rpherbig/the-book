from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

while True:
    user_input = input("Enter the user prompt (or type 'exit' to quit):")
    if user_input.lower() == "exit":
        break

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content":
                """
                You are a customer service chatbot designed to be helpful and answer user's questions if possible.
                The phone number for the Maintenance & Service department is (555) 555-1234.
                The phone number for the Customer Support department is (555) 555-5678.
                The phone number for the Dealer Service department is (555) 555-9012.
                The hours of operation for the Maintenance & Service department are 7am-7pm every day.
                The hours of operation for the Customer Support department are 8am-5pm every weekday.
                The hours of operation for the Dealer Service department are 7am-6pm every weekday and noon-5pm on Saturdays.
                """
                # If you do not know the answer, apologize and suggest the user contact Customer Support for additional help. Provide the phone number and hours of operation.
            },
            {"role": "user", "content": user_input},
        ]
    )
    print(completion.choices[0].message.content)
