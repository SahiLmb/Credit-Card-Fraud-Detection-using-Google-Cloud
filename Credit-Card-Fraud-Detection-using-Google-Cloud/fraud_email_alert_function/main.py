import base64
import json
import smtplib
from google.cloud import secretmanager
from json import loads
from email.mime.text import MIMEText
from email.header import Header

# Strict cleaner for all fields
def clean(text):
    if isinstance(text, str):
        return text.replace('\xa0', ' ').replace('\u00a0', ' ').strip()
    return str(text)

def hello_pubsub(event, context):
    # Load SMTP credentials from Secret Manager
    secret_client = secretmanager.SecretManagerServiceClient()
    project_id = "your_project_id"
    secret_response = secret_client.access_secret_version(
        {"name": f"projects/{project_id}/secrets/smtp_credentials/versions/latest"}
    )
    my_credentials = loads(secret_response.payload.data.decode("utf-8"))

    smtp_email = clean(my_credentials["serv_mail"])
    smtp_password = clean(my_credentials["password"])

    # Parse the Pub/Sub message
    pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
    message_json = json.loads(pubsub_message)

    # Email mapping
    customer_email_pairs = [
        {"senders_name": "Kathryn Williams", "email": "bodkesahil26@gmail.com"},
        {"senders_name": "Tiffany Holloway", "email": "work.bodke@gmail.com"},
        {"senders_name": "Peter Perez", "email": "bodkesahil26@gmail.com"},
        {"senders_name": "Sandra Sanchez", "email": "work.bodke@gmail.com"},
        {"senders_name": "Jennifer Kirby", "email": "bodkesahil26@gmail.com"},
        {"senders_name": "James Ward", "email": "work.bodke@gmail.com"},
        {"senders_name": "Kyle Palmer", "email": "bodkesahil26@gmail.com"},
        {"senders_name": "Margaret Maldonado", "email": "work.bodke@gmail.com"},
        {"senders_name": "Frank Garcia", "email": "bodkesahil26@gmail.com"},
        {"senders_name": "Katie Romero", "email": "work.bodke@gmail.com"}
    ]

    bank_email_pairs = [
        {"SendersBank": "ICICI Bank", "email": "bodkesahil26@gmail.com"},
        {"SendersBank": "Barclays", "email": "work.bodke@gmail.com"},
        {"SendersBank": "Kotak Mahindra Bank", "email": "bodkesahil26@gmail.com"},
        {"SendersBank": "HSBC", "email": "work.bodke@gmail.com"},
        {"SendersBank": "HDFC Bank", "email": "bodkesahil26@gmail.com"},
        {"SendersBank": "Standard Chartered", "email": "work.bodke@gmail.com"},
        {"SendersBank": "Union Bank of India", "email": "bodkesahil26@gmail.com"},
        {"SendersBank": "State Bank of India", "email": "work.bodke@gmail.com"},
        {"SendersBank": "Bank of Baroda", "email": "bodkesahil26@gmail.com"},
        {"SendersBank": "Punjab National Bank", "email": "work.bodke@gmail.com"}
    ]

    senders_name = clean(message_json["senders_name"])
    SendersBank = clean(message_json["SendersBank"])

    customer_email = next((p["email"] for p in customer_email_pairs if clean(p["senders_name"]) == senders_name), "bodkesahil26@gmail.com")
    bank_email = next((p["email"] for p in bank_email_pairs if clean(p["SendersBank"]) == SendersBank), "work.bodke@gmail.com")

    # Email content
    email_subject_customer = clean("Fraud Alert: Suspicious Activity on Your Account")
    email_body_customer = f"""
Dear {senders_name},

We have identified a suspicious transaction on your account that appears to be fraudulent. Please review the transaction details below:

- Type: {clean(message_json['type'])}
- Transaction ID: {clean(message_json['id'])}
- Amount: Rs. {clean(message_json['amount'])}
- Old Balance (Origin): Rs. {clean(message_json['oldbalanceOrig'])}
- New Balance (Origin): Rs. {clean(message_json['newbalanceOrig'])}
- Old Balance (Destination): Rs. {clean(message_json['oldbalanceRec'])}
- New Balance (Destination): Rs. {clean(message_json['newbalanceRec'])}
- Country: {clean(message_json['Country'])}
- Sender's Bank: {clean(message_json['SendersBank'])}
- Receiver's Bank: {clean(message_json['ReceiversBank'])}
- Receiver Name: {clean(message_json['receiver_name'])}
- Transaction Date: {clean(message_json['TransactionDates'])}

If you do not recognize this transaction, please contact our fraud helpline immediately at 1800-1800.

Regards,  
Fraud Prevention Unit  
TransactionPe Ltd.
"""

    email_subject_bank = clean("Urgent: Fraudulent Transaction Flagged from Your Institution")
    email_body_bank = f"""
Dear Security Team,

A potentially fraudulent transaction has been detected involving an account holder from your bank. Please review the transaction details below for immediate investigation:

- Type: {clean(message_json['type'])}
- Transaction ID: {clean(message_json['id'])}
- Amount: Rs. {clean(message_json['amount'])}
- Origin Account (Old Balance): Rs. {clean(message_json['oldbalanceOrig'])}
- Origin Account (New Balance): Rs. {clean(message_json['newbalanceOrig'])}
- Destination Account (Old Balance): Rs. {clean(message_json['oldbalanceRec'])}
- Destination Account (New Balance): Rs. {clean(message_json['newbalanceRec'])}
- Country: {clean(message_json['Country'])}
- Sender's Name: {clean(message_json['senders_name'])}
- Sender's Bank: {clean(message_json['SendersBank'])}
- Receiver's Bank: {clean(message_json['ReceiversBank'])}
- Receiver Name: {clean(message_json['receiver_name'])}
- Date: {clean(message_json['TransactionDates'])}

Kindly take necessary action as per compliance policy.

Best Regards,  
Risk & Compliance Department  
TransactionPe Ltd.
"""

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)

            msg_to_customer = MIMEText(email_body_customer, "plain", "utf-8")
            msg_to_customer["Subject"] = str(Header(email_subject_customer, "utf-8"))
            msg_to_customer["From"] = smtp_email
            msg_to_customer["To"] = customer_email

            msg_to_bank = MIMEText(email_body_bank, "plain", "utf-8")
            msg_to_bank["Subject"] = str(Header(email_subject_bank, "utf-8"))
            msg_to_bank["From"] = smtp_email
            msg_to_bank["To"] = bank_email

            server.send_message(msg_to_customer)
            server.send_message(msg_to_bank)

        print("Emails sent successfully.")
    except Exception as e:
        print("Error sending emails:", str(e))

    print(pubsub_message)
