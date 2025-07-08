# 🚨 Real-Time Credit Card Fraud Detection on Google Cloud

This project implements a scalable real-time fraud detection system for financial transactions using Google Cloud services. The system classifies transactions as fraudulent or non-fraudulent, stores them accordingly, and triggers alerts to stakeholders.

---

## 🔧 Toolbox
![tools](https://github.com/SahiLmb/Credit-Card-Fraud-Detection-using-Google-Cloud/blob/main/Diagrams/tools%20used.jpg)

## Overview of Tools and Their Roles

- **BigQuery ML** – For training the fraud detection model using SQL.
- **Pub/Sub** – For ingesting and transmitting streaming transaction data.
- **Dataflow** – For real-time data processing and writing to Firestore & BigQuery.
- **Cloud Firestore** – Temporary storage of transaction records for quick access.
- **BigQuery** – Permanent storage and ML model training/prediction.
- **Cloud Functions** – For predictions and fraud alert automation.
- **Cloud Scheduler** – To periodically trigger batch predictions.
- **Secret Manager** – To store and access email credentials securely.
- **Looker Studio** – For building fraud monitoring dashboards.
- **SMTP via Gmail** – For sending alert emails to banks and customers.

---

## 📈 Architecture Workflow

### 1. 📨 Data Ingestion
- A Python script simulates new credit card transactions.
- These transactions are published to the **`credit_card_transactions`** Pub/Sub topic.

### 2. 🔄 Real-Time Processing with Dataflow
- Reads messages from the Pub/Sub topic.
- Writes raw transaction data to:
  - **Cloud Firestore** (real-time view)
  - **BigQuery temp table** (`temp_transaction_input`)

### 3. 🧠 ML Model Prediction
- Every 5 minutes, a **Cloud Scheduler** triggers a **Cloud Function**:
  - Invokes BigQuery ML's `ML.PREDICT()` on new transactions.
  - Writes predictions to:
    - `bigquery_fraud_data_table`
    - `bigquery_non_fraud_data_table`

### 4. 🚨 Fraud Alert Pipeline
- A second **Cloud Function** fetches recent fraud predictions and:
  - Publishes to **`fraud_alerts`** Pub/Sub topic.
  - Sends alert emails to sender/receiver banks using **SMTP (Gmail)**.
  - Uses credentials stored in **Secret Manager**.

### 5. 📊 Dashboard & Insights
- Data from both BigQuery tables is visualized using **Looker Studio**:
  - Real-time and historical fraud patterns.
  - KPIs: Total/Fraud transactions, fraud amount, fraud rates, risky receivers, etc.

---

## 🧱 System Components

| Component            | Description |
|---------------------|-------------|
| **Pub/Sub**          | Streams incoming transactions |
| **Dataflow**         | Reads from Pub/Sub and writes to Firestore & BigQuery |
| **BigQuery**         | Stores data and hosts the ML model |
| **BigQuery ML**      | Trains fraud detection model (`BOOSTED_TREE_CLASSIFIER`) |
| **Cloud Scheduler**  | Triggers model inference every 5 mins |
| **Cloud Functions**  | Executes fraud prediction logic and sends alerts |
| **Secret Manager**   | Secures email credentials |
| **Firestore**        | Stores live transactions |
| **Looker Studio**    | Visualizes fraud analytics |

---

## 🖼️ Architecture Diagram

![Architecture Diagram](https://github.com/SahiLmb/Credit-Card-Fraud-Detection-using-Google-Cloud/blob/main/Diagrams/Gcloud%20Architecute%20Fraud%20Detection.jpg)

---

## 🧪 Prediction Cloud Function Logic (Summary)
- Run `ML.PREDICT` on `temp_transaction_input`
- Write to fraud/non-fraud BigQuery tables
- Publish recent fraud results to Pub/Sub (`fraud_alerts`)
- Clean temp table

---

## 📬 Email Alerts
- Sent via **SMTP Gmail** to:
  - Fraudulent transaction sender and receiver banks
  - Customers
- Configured with **secure credentials via Secret Manager**

---

## 📊 Dashboard Highlights

- Top 5 Receivers involved in Fraud
- Fraud Count vs Amount by Type
- Country-wise fraud trends
- Year-wise fraud activity
- Repeated fraudulent receivers

🔗 **[Dashboard Link](https://lookerstudio.google.com/reporting/abd9c51b-984e-4b45-a12b-86cf08bbdabe)**

![Dashboard page 1](https://github.com/SahiLmb/Credit-Card-Fraud-Detection-using-Google-Cloud/blob/main/Snapshots/Fraud_Detection_Analysis_page-0001.jpg)

![Dashboard page 2](https://github.com/SahiLmb/Credit-Card-Fraud-Detection-using-Google-Cloud/blob/main/Snapshots/Fraud_Detection_Analysis_page-0002.jpg)


## Email to Bank
![bank mail](https://github.com/SahiLmb/Credit-Card-Fraud-Detection-using-Google-Cloud/blob/main/Snapshots/bank%20mail.png)

## Email to Customer
![customer mail](https://github.com/SahiLmb/Credit-Card-Fraud-Detection-using-Google-Cloud/blob/main/Snapshots/user%20mail.png)

## **Code Structure**
```plaintext
├── Home Directory  
|   ├── Dataflow_pipeline.py
|   ├── Pubsub_Transactions.py
|   ├── fraud_data.csv
|   ├── requirements.txt
```

## **Conclusion**
This end-to-end credit card fraud detection system showcases the power of integrating Google Cloud services to build a scalable, real-time fraud detection pipeline. By leveraging BigQuery ML for model training, Dataflow for streaming data processing, Pub/Sub for event-driven architecture, Firestore for intermediate storage, and Looker Studio for visual analytics, the system offers a seamless workflow from data ingestion to fraud alerting.

### Key highlights include:

- Real-time fraud prediction with automated notifications to banks and customers.

- Secure handling of sensitive credentials using Secret Manager.

- Interactive dashboards for transaction monitoring and actionable insights.

This architecture not only helps detect fraudulent activity efficiently but also serves as a strong foundation for similar use cases across industries such as insurance fraud, transaction risk scoring, or anomaly detection systems.


