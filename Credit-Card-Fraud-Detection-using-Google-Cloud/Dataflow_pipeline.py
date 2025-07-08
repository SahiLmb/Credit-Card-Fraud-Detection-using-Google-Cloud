import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import json
from datetime import datetime
from google.cloud import firestore

class StoreToFirestoreAndBQ(beam.DoFn):
    def __init__(self, project):
        self.project = project

    def setup(self):
        self.firestore = firestore.Client(project=self.project)

    def process(self, element):
        data = json.loads(element.decode('utf-8'))

        # Adding created_at timestamp
        data["created_at"] = datetime.utcnow().isoformat()

        # Firestore insert
        doc_id = f"txn_{data['id']}"
        self.firestore.collection('transactions').document(doc_id).set(data)

        yield data  # Passing to BigQuery

def run():
    project = "your-project-id"  # 🔐 Replace with your GCP project ID

    schema = """
        type:STRING,
        id:STRING,
        amount:FLOAT,
        oldbalanceOrig:FLOAT,
        newbalanceOrig:FLOAT,
        oldbalanceRec:FLOAT,
        newbalanceRec:FLOAT,
        Country:STRING,
        senders_name:STRING,
        ReceiversBank:STRING,
        SendersBank:STRING,
        receiver_name:STRING,
        TransactionDates:STRING,
        isFraud:INTEGER,
        created_at:TIMESTAMP
    """

    options = PipelineOptions(streaming=True, save_main_session=True)
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read from PubSub" >> beam.io.ReadFromPubSub(subscription="projects/your-project-id/subscriptions/your-subscription-id")
            | "Process and Store" >> beam.ParDo(StoreToFirestoreAndBQ(project))
            | "Write to BQ temp table" >> beam.io.WriteToBigQuery(
                table="your-project-id:your_dataset.temp_transaction_input",
                schema=schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == "__main__":
    run()
