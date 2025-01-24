# Cloudwalk

## Software Engineer Test

### Transactional Sample Case

#### Description

This project addresses the case provided at [link](https://gist.github.com/cloudwalk-tests/76993838e65d7e0f988f40f1b1909c97#file-transactional-sample-csv).  
The objective is to efficiently analyze and process transactional data, extracting relevant insights and demonstrating skills in data manipulation and database management.

---

#### Repository Structure

- **`transactional_sample.csv`**: Data file provided for the case.
- **`script.ipynb`**: Python script in Jupyter Notebook format that:
  1. Loads the CSV data into a DataFrame.
  2. Performs basic transformations and analysis.
  3. Inserts the processed data into a PostgreSQL database.
- **`README.md`**: Instructions and detailed information about the project.
- **`app_api_transacoes_unitarias.py`**: Fraud detection API implemented in Flask that evaluates individual transactions.
- **`avaliador_transacoes.py`**: Script that processes batch transactions and sends data to the API for evaluation.
- **`cliente.py`**: Client script that sends individual transactions to the API for evaluation.

---

#### Technologies Used

1. PostgreSQL Database:
   * Hosted on AWS RDS.
   * Contains the tables ``transactions``, ``transactions_log``, and ``transactions_api_results``.

2. Metabase:
   * Hosted on AWS EC2.
   * Connected to the database to create dashboards and execute SQL queries.

3. Python:
   * Exploratory analysis, API development, and automation testing.

4. Flask:
   * Framework used for API implementation.

5. SQLAlchemy:
   * Manages database connections and queries.

---

#### Database

- Table Structure

1. ``transactions`` Table: Stores the original transactional data.

```sql
CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY,
    merchant_id BIGINT,
    user_id BIGINT,
    card_number VARCHAR(16),
    transaction_date TIMESTAMP,
    transaction_amount DOUBLE PRECISION,
    device_id BIGINT,
    has_cbk BOOLEAN
);
```

2. ``transactions_log`` Table: Stores all transactions evaluated by the API, including applied rules and the final decision. Before running the API, data from the ``transactions`` table was inserted into this table with the ``rule_applied`` column set to ``default`` in cases where the transaction had already been evaluated. This ensures a historical record for future transaction evaluations.

```sql
CREATE TABLE transactions_log (
    transaction_id TEXT PRIMARY KEY,          -- Unique transaction identifier
    user_id TEXT NOT NULL,                    -- User ID
    merchant_id TEXT NOT NULL,                -- Merchant ID
    card_number TEXT NOT NULL,                -- Card number
    transaction_date TIMESTAMP NOT NULL,      -- Transaction date and time
    transaction_amount NUMERIC NOT NULL,      -- Transaction amount
    device_id TEXT,                           -- Device ID
    recommendation TEXT NOT NULL,             -- "approve" or "deny"
    rule_applied TEXT,                        -- Rule responsible for the decision
    created_at TIMESTAMP DEFAULT NOW()        -- Log entry date
);
```

```sql
INSERT INTO transactions_log (
    transaction_id, user_id, merchant_id, card_number,
    transaction_date, transaction_amount, device_id,
    has_chargeback, recommendation, rule_applied
)
SELECT
    transaction_id, user_id, merchant_id, card_number,
    transaction_date, transaction_amount, device_id,
    has_cbk AS has_chargeback,                              -- Existing chargeback status
    CASE                                                    -- Generate initial recommendation based on chargeback status
        WHEN has_cbk = TRUE THEN 'deny'
        ELSE 'approve'
    END AS recommendation,
    'historical_chargeback' AS rule_applied                 -- Mark as historical data
FROM transactions;
```

3. ``transactions_api_results`` Table: Stores test results performed by the API for later validation.

```sql
CREATE TABLE transactions_api_results (
    transaction_id BIGINT PRIMARY KEY,
    has_cbk BOOLEAN,
    recommendation VARCHAR(20),
    rule_applied VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

#### Prerequisites

Make sure you have the following tools installed:

- **Python 3.8+**: To run the script.
- **PostgreSQL**: To store the processed data.
- **Python Libraries**:
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `sqlalchemy`
  - `sklearn.preprocessing`
  - `Flask`
  - `psycopg2`
  - `requests`
  - `concurrent.futures`  
  - `python-dotenv` (to load environment variables from the `.env` file)
- **Virtual Environment**:
   - Recommended to isolate project dependencies.

---

#### Virtual Environment Setup

1. **Create the Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

#### Installation and Configuration

1. Clone the repository:
   ```bash
   git clone https://github.com/Thallysbatista/cloudwalk.git
   cd cloudwalk-test
   ```

2. Create a `.env` file in the project root with the following variables:
   ```env
   DB_HOST=url_host
   DB_NAME=database_name
   DB_USER=username
   DB_PASSWORD=database_password
   DB_PORT=5432
   ```

---

#### How to Run the Project

1. **Execute the SQL scripts to create the tables.**

2. **Start the API server**
   ```bash
   python app_api_transacoes_unitarias.py
   ```

3. **Process batch transactions and insert into the database**
   ```bash
   python avaliador_transacoes.py
   ```

4. **Send an individual transaction to the API**
   ```bash
   python cliente.py
   ```

5. **Analysis in Metabase:**
   [Link to dashboard](http://18.117.137.2:3000/public/dashboard/461921e1-81d7-47ca-9abf-5e59f38400fb)

---

#### Testing and Validation

1. **Automated Batch Testing:**
   - The ``avaliador_transacoes.py`` script processes existing data from the transactions table and sends them to the API.
   - Results are stored in the ``transactions_api_results`` table for future comparison.

2. **Unit Testing with Individual Transactions:**
   - The ``cliente.py`` script allows sending individual transactions to be evaluated by the API.
   - This facilitates validation of specific scenarios.

3. **Accuracy:**
   - The API's effectiveness is evaluated by comparing the actual chargeback status ``(has_cbk)`` with the API's recommendation ``(recommendation)``.

---

#### Fraud Detection API

The API is designed to receive transaction information, evaluate it based on predefined rules, and return a recommendation to "approve" or "deny".

- **Implemented Rules**

1. **Chargeback History:**
   - Deny transactions from users, merchants, or cards with a chargeback history.

2. **High Value and Critical Hours:**
   - Deny transactions above R$ 1800 made between 8 PM and 4 AM.

3. **Transaction Frequency:**
   - Deny transactions from devices that made more than 3 transactions in 1 hour, with a total amount exceeding R$ 2500.

4. **Default Approval:**
   - Transactions that do not meet the above criteria are approved.

---

#### Final Considerations

This project aims to demonstrate the ability to implement a solution for fraud detection in financial transactions using Python, Flask, and PostgreSQL. The fraud detection API was developed to be scalable, efficient, and easily adjustable to new business rules. Additionally, the integration with Metabase facilitates result analysis and insight generation for decision-making.
