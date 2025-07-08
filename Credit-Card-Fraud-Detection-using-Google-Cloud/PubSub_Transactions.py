import csv
import time
import json
from google.cloud import pubsub_v1

# ✅ Setting GCP details
project_id = 'cred-462105'  # <- replace with actual project ID
topic_name = 'credit-card-transactions'  # <- must exist in Pub/Sub

# ✅ Pub/Sub publisher client setup
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# ✅ file path (CSV with 20000 records)
filename = 'fraud_transactions_20000.csv'  # <- adjust path if needed

# ✅ Delay in seconds between records (can reduce to 1–2 sec if testing)
time_delay = 2  # <- adjust as needed


# ✅ Open CSV and send each record
with open(filename, 'r') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        data = {
            'type': row['type'],
            'id': row['id'],
            'amount': float(row['amount']),
            'oldbalanceOrig': float(row['oldbalanceOrig']),
            'newbalanceOrig': float(row['newbalanceOrig']),
            'oldbalanceRec': float(row['oldbalanceRec']),
            'newbalanceRec': float(row['newbalanceRec']),
            'Country': row['Country'],
            'senders_name': row['senders_name'],
            'ReceiversBank': row['ReceiversBank'],
            'SendersBank': row['SendersBank'],
            'receiver_name': row['receiver_name'],
            'TransactionDates': row['TransactionDates'],
            'isFraud': 1 if row['isFraud'].lower() in ['1', 'true', 'yes'] else 0
 # Cast to int if needed for ML
        }

        # Convert to bytes and publish
        message_data = json.dumps(data).encode('utf-8')
        future = publisher.publish(topic_path, data=message_data)
        
        print("Published:", data)
        try:
            message_id = future.result()
            print(f"✅ Message ID: {message_id}")
        except Exception as e:
            print(f"❌ Failed to publish: {e}")

        time.sleep(time_delay)
