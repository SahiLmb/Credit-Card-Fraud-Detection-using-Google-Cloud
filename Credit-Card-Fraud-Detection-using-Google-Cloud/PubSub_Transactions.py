import csv
import time
import json
from google.cloud import pubsub_v1

# ✅ Setting GCP details
project_id = 'your-project-id'  # 🔐 Replace with your actual GCP project ID
topic_name = 'your-topic-name'  # 🔐 Replace with your existing Pub/Sub topic

# ✅ Pub/Sub publisher client setup
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# ✅ File path (CSV with transaction records)
filename = 'your-transaction-data.csv'  # 🔐 Replace with your actual CSV file path

# ✅ Delay in seconds between records
time_delay = 2  # Adjust based on real-time simulation speed

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
        }

        # Convert to bytes and publish
        message_data = json.dumps(data).encode('utf-8')
        future = publisher.publish(topic_path, data=message_data)
        
        print("📤 Published:", data)
        try:
            message_id = future.result()
            print(f"✅ Message ID: {message_id}")
        except Exception as e:
            print(f"❌ Failed to publish: {e}")

        time.sleep(time_delay)
