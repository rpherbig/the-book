from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

test_cases = {
    "How do I contact the Maintenance & Service department?" : "The phone number for the Maintenance & Service department is (555) 555-1234. Their hours of operation are from 7am to 7pm every day.",
    "How do I contact the Customer Support department?" : "The phone number for the Customer Support department is (555) 555-5678. Their hours of operation are from 8am to 5pm every weekday.",
    "How do I contact the Dealer Service department?" : "The phone number for the Dealer Service department is (555) 555-9012. Their hours of operation are from 7am-6pm every weekday and noon-5pm on Saturdays.",
}

for question, expected_answer in test_cases.items():
    print("----------")
    print(f"question: {question}")
    print(f"expected_answer: {expected_answer}")
    # Generate the actual answer for the chatbot
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
                If you do not know the answer, apologize and suggest the user contact Customer Support for additional help. Provide the phone number and hours of operation.
                """
            },
            {"role": "user", "content": question},
        ]
    )
    actual_answer = completion.choices[0].message.content
    print(f"actual_answer: {actual_answer}")

    # Fact-check the chatbot's answer
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content":
                f"""
                You will be provided with a user question and a generated answer that is supposed to answer the question.
                
                Reason about whether the information in the generated answer is based on the following pieces of information:
                - The phone number for the Maintenance & Service department is (555) 555-1234.
                - The phone number for the Customer Support department is (555) 555-5678.
                - The phone number for the Dealer Service department is (555) 555-9012.
                - The hours of operation for the Maintenance & Service department are 7am-7pm every day.
                - The hours of operation for the Customer Support department are 8am-5pm every weekday.
                - The hours of operation for the Dealer Service department are 7am-6pm every weekday and noon-5pm on Saturdays.

                If the answer correctly answers the question, write "True", otherwise write "False". Do not write anything else.

                The user question is: {question}

                The generated answer is: {actual_answer}
                """
            },
        ]
    )
    fact_check_result = completion.choices[0].message.content
    print(f"fact_check_result: {fact_check_result}")

    # Compare the chatbot's answer to an expected answer from an expert
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content":
                f"""
                You will be provided with a user question, a generated answer, and an expert's answer.
                
                Reason about whether the information in the generated answer compared to the expert answer is either: disjoint, equal, a subset, a superset, or overlapping (i.e. some intersection but not subset/superset).
                
                Reason about whether the submitted answer contradicts any aspect of the expert answer.

                Output only the type of overlap ("disjoint" or "equal" or "subset" or "superset" or "overlapping") and if there is a contradiction (True or False).

                The user question is: {question}

                The generated answer is: {actual_answer}

                The expert's answer is: {expected_answer}
                """
            },
        ]
    )
    comparison_result = completion.choices[0].message.content
    print(f"comparison_result: {comparison_result}")
