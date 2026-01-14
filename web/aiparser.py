from email import message
import os
from google import genai
from dotenv import load_dotenv


load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No key found")
client = genai.Client(api_key=api_key)


def gemini_transaction_parser(sms_data):
    
    message_content = sms_data.get('message') or sms_data.get('messages') or ""
    sender_name = sms_data.get('sender') or sms_data.get('senders') or "Unknown"

    prompt = f"""
    You are an expert financial data analyst specializing in Malawi's fintech ecosystem.
    Your task is to extract transaction details from SMS messages.

    CONTEXT:
    - Mobile Money: Airtel Money, TNM Mpamba , etc.
    - Banks: Standard Bank (247), National Bank (626), FDH, MyBucks , etc.
    - Remittance: Mukuru, HelloPaisa, WorldRemit , etc.

    EXAMPLES FOR TRAINING:
    1. BANK (Standard Bank): "Txn: Payment of MK50,000.00 from ACCT **123 to AGNESS MWIMANIWA on 14/01/2026 10:30. Ref: School Fees. Bal: MK120,000.00"
       -> {{"source": "Standard Bank", "type": "BANK_TRANSFER", "direction": "OUTGOING", "amount": 50000.0}}
    2. REMITTANCE (Mukuru): "Mukuru: Order 12345678 collected. Amount: MK85,000.00. Thank you for using Mukuru."
       -> {{"source": "Mukuru", "type": "REMITTANCE", "direction": "INCOMING", "amount": 85000.0}}

    SMS TO PARSE:
    SENDER: {sender_name}
    MESSAGE: {message_content}

    STRICT JSON STRUCTURE:
    {{
        "source": string,           // e.g., "AirtelMoney", "Standard Bank", "Mukuru"
        "type": string,             // "CASH_OUT", "CASH_IN", "PAYMENT", "AIRTIME", "BANK_TRANSFER", "REMITTANCE"
        "direction": string,        // "INCOMING", "OUTGOING", or null
        "amount": float,            // Numeric only
        "fees": float,              // Extract if mentioned, else 0.0
        "currency": "MWK",          // Default to MWK for Malawi
        "counterparty": string,     // Name of person/shop
        "reference": string,        // Trans ID or Ref note
        "timestamp": "YYYY-MM-DD HH:MM:SS",
        "raw_text": string
    }}

    Return ONLY the JSON. No conversational text.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt,
        config={ "response_mime_type": "application/json" }
    )
    return response.text

if __name__ == "__main__":
    # Example usage
    print(gemini_transaction_parser({"sender": "AirtelMoney", "message": "You have sent MK10,000.00 to John Doe. Ref: Rent. Fees: MK100.00. New balance: MK50,000.00"}))