import datetime
import os
import json
import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def gemini_transaction_parser(sms_dict, uid):
    """
    Parses a dictionary of SMS messages into a structured financial JSON list.
    """
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert dictionary to JSON string for the prompt
    formatted_sms_data = json.dumps(sms_dict, indent=2)

    prompt = f"""
    Context: Expert Financial Analyst for Malawi (Airtel Money, TNM Mpamba, National Bank 626, Standard Bank 247).
    Current Reference Time: {now}
    User ID: {uid}

    INPUT DATA:
    {formatted_sms_data}

    YOUR TASKS:
    1. FILTER: Ignore all non-financial messages (OTP codes, KYC updates, "Moto kuti Buu" promos, app registrations).
    2. SOURCE MAPPING: 
       - If sender is "626626" -> Source: "National Bank"
       - If sender is "247" -> Source: "Standard Bank"
       - Otherwise, use the Sender name (e.g., "AirtelMoney").
    3. EXTRACTION: Convert messy dates (e.g., 14/01) into "YYYY-MM-DD HH:MM:SS" using the reference year 2026.
    4. LOANS: Identify "Kutapa" or "Airtime loans" as type "LOAN".

    STRICT OUTPUT FORMAT:
    Return a JSON LIST of objects only. Each object must follow this structure:
    {{
        "source": string,
        "type": "CASH_OUT" | "CASH_IN" | "PAYMENT" | "AIRTIME" | "BANK_TRANSFER" | "REMITTANCE" | "LOAN",
        "direction": "INCOMING" | "OUTGOING",
        "amount": float,
        "fees": float,
        "currency": "MWK",
        "counterparty": string,
        "reference": string,
        "timestamp": "YYYY-MM-DD HH:MM:SS"
    }}

    If NO transactions are found in the data, return an empty list: [].
    """

    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            }
        )
        
        # Clean up and return the result
        return response.text
        
    except Exception as e:
        print(f"AI Parser Error: {e}")
        return "[]" # Return empty list i hate 404s



if __name__ == "__main__":
    
    print(gemini_transaction_parser({"sender": "AirtelMoney", "message": "You have sent MK10,000.00 to John Doe. Ref: Rent. Fees: MK100.00. New balance: MK50,000.00"}))