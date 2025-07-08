from google.cloud import bigquery, pubsub_v1
from datetime import datetime
import json

def run_prediction(request):
    bq_client = bigquery.Client()
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path("your-project-id", "your-topic-name")  # 🔐 Replace with your Pub/Sub topic

    # Step 1: Run predictions and insert into fraud/non-fraud tables
    prediction_query = """
    CREATE OR REPLACE TABLE `your-dataset.temp_predictions` AS
    SELECT * EXCEPT(predicted_isFraud),
           predicted_isFraud
    FROM ML.PREDICT(
      MODEL `your-dataset.boosted_tree_model_tuned`,
      (
        SELECT *
        FROM `your-dataset.temp_transaction_input`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE)
      )
    );

    INSERT INTO `your-dataset.bigquery_fraud_data_table` (
      type, id, amount, oldbalanceOrig, newbalanceOrig,
      oldbalanceRec, newbalanceRec, Country, senders_name,
      ReceiversBank, SendersBank, receiver_name, TransactionDates,
      isFraud, predicted_isFraud, created_at
    )
    SELECT
      type, id, amount, oldbalanceOrig, newbalanceOrig,
      oldbalanceRec, newbalanceRec, Country, senders_name,
      ReceiversBank, SendersBank, receiver_name, TransactionDates,
      isFraud, predicted_isFraud, CURRENT_TIMESTAMP()
    FROM `your-dataset.temp_predictions`
    WHERE predicted_isFraud = 1;

    INSERT INTO `your-dataset.bigquery_non_fraud_data_table` (
      type, id, amount, oldbalanceOrig, newbalanceOrig,
      oldbalanceRec, newbalanceRec, Country, senders_name,
      ReceiversBank, SendersBank, receiver_name, TransactionDates,
      isFraud, predicted_isFraud, created_at
    )
    SELECT
      type, id, amount, oldbalanceOrig, newbalanceOrig,
      oldbalanceRec, newbalanceRec, Country, senders_name,
      ReceiversBank, SendersBank, receiver_name, TransactionDates,
      isFraud, predicted_isFraud, CURRENT_TIMESTAMP()
    FROM `your-dataset.temp_predictions`
    WHERE predicted_isFraud = 0;
    """

    job = bq_client.query(prediction_query)
    job.result()

    # Step 2: Fetch recent fraud entries and publish to Pub/Sub
    fraud_rows = bq_client.query("""
        SELECT *
        FROM `your-dataset.bigquery_fraud_data_table`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 MINUTE)
    """).result()

    def serialize_row(row):
        result = {}
        for key, value in dict(row).items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

    for row in fraud_rows:
        message = json.dumps(serialize_row(row))
        publisher.publish(topic_path, data=message.encode("utf-8"))

    # Step 3: Truncate temporary table
    bq_client.query("TRUNCATE TABLE `your-dataset.temp_predictions`").result()

    return "Prediction completed and fraud alerts published", 200
