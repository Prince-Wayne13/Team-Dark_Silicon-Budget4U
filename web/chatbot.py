import datetime
import os 
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def chatbot_response(user_input):
    system_prompt = """
                    # ROLE
                    Friendly AI Financial Advisor for Malawi. Focus: Airtel Money, TNM Mpamba, National Bank, Standard Bank.

                    # DATA GROUNDING
                    Analyze ONLY provided JSON transactions (source, type, amount MWK, counterparty, timestamp).
                    - Never guess or hallucinate. 
                    - If data is missing or query is non-financial, say: "I don't have that data" or "I only discuss finances."

                    # MALAWI CONTEXT
                    - Recognize: Kutapa/Airtime loans, ESCOM tokens, Masm, and mobile money fees.
                    - Treat loans as high-priority debt.

                    # TASKS
                    1. Analyze spend trends & hidden fees.
                    2. Track goals with real math.
                    3. Suggest repayment for expensive loans.

                    # STYLE
                    - Simple language. **Bold** all MWK amounts.
                    - End with exactly ONE actionable next step (e.g., "Set a limit of **MK5,000**?").
                    """

    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=user_input,
            config={
                "max_output_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "system_instruction": system_prompt
                }
        )

                            
        
    except Exception as e:
        
        print(f"Error generating chatbot response: {e}") 

    return response.text

if __name__ == "__main__":
    user_input = "Show me my spending summary for last month."
    print(chatbot_response(user_input))