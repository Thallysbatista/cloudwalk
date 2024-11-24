# Este script permitirá receber transações do script cliente e avaliar essas transações.

from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import pool
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração do pool de conexões com o PostgreSQL usando as variáveis de ambiente
db_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    database=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    host=os.environ.get('DB_HOST'),
    password=os.environ.get('DB_PASSWORD'),
    port=os.environ.get('DB_PORT')
)

# Função para obter uma conexão do pool
def get_db_connection():
    try:
        conn = db_pool.getconn()
        return conn
    except Exception as e:
        logger.error(f"Erro ao obter conexão do pool: {e}")
        raise

# Função para liberar a conexão de volta ao pool
def release_db_connection(conn):
    try:
        db_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Erro ao liberar conexão do pool: {e}")

# Função para verificar histórico de chargebacks
def check_chargeback_history(conn, user_id, merchant_id, card_number):
    with conn.cursor() as cursor:
        query = """
            SELECT DISTINCT has_chargeback
            FROM transactions_log
            WHERE (CAST(user_id AS TEXT) = %s OR CAST(merchant_id AS TEXT) = %s OR card_number = %s)
              AND has_chargeback = TRUE;
        """
        cursor.execute(query, (str(user_id), str(merchant_id), card_number))
        result = cursor.fetchone()
        return result[0] if result else False

# Função para verificar valores elevados e horários críticos
def check_high_value_and_time(transaction_amount, transaction_date):
    time_hour = transaction_date.hour
    if transaction_amount > 1800 and (20 <= time_hour or time_hour < 4):
        return True
    return False

# Função para verificar frequência de transações por dispositivo
def check_frequency_and_value(conn, device_id, current_time):
    if device_id is None:
        return False  # Não pode verificar frequência sem device_id

    with conn.cursor() as cursor:
        query = """
            SELECT COUNT(*) AS transaction_count, SUM(transaction_amount) AS total_value
            FROM transactions_log
            WHERE CAST(device_id AS TEXT) = %s 
              AND transaction_date >= (%s::timestamp - interval '1 hour');
        """
        cursor.execute(query, (str(device_id), current_time))
        result = cursor.fetchone()

        # Verificar regras de frequência e valor
        transaction_count = result[0] if result else 0
        total_value = result[1] if result else 0
        if transaction_count > 3 and total_value > 2500:
            return True
        return False

# Função para salvar transação no log
def save_transaction_log(conn, data, recommendation, rule_applied, has_chargeback):
    with conn.cursor() as cursor:
        query = """
            INSERT INTO transactions_log (
                transaction_id, user_id, merchant_id, card_number,
                transaction_date, transaction_amount, device_id,
                recommendation, rule_applied, has_chargeback
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO UPDATE SET
                recommendation = EXCLUDED.recommendation,
                rule_applied = EXCLUDED.rule_applied,
                has_chargeback = EXCLUDED.has_chargeback;
        """
        cursor.execute(query, (
            data.get("transaction_id"),
            data.get("user_id"),
            data.get("merchant_id"),
            data.get("card_number"),
            data.get("transaction_date"),
            data.get("transaction_amount"),
            data.get("device_id"),
            recommendation,
            rule_applied,
            has_chargeback
        ))
    conn.commit()

@app.route('/evaluate_transaction', methods=['POST'])
def evaluate_transaction():
    # Receber o payload
    data = request.get_json()
    user_id = data.get('user_id')
    merchant_id = data.get('merchant_id')
    card_number = data.get('card_number')
    transaction_amount = data.get('transaction_amount')
    transaction_date_str = data.get('transaction_date')
    device_id = data.get('device_id')

    conn = None

    try:
        # Converter transaction_date para datetime
        transaction_date = datetime.fromisoformat(transaction_date_str)

        # Estabelecer conexão com o banco de dados
        conn = get_db_connection()

        # 1. Verificar histórico de chargebacks
        has_chargeback = check_chargeback_history(conn, user_id, merchant_id, card_number)
        if has_chargeback:
            recommendation = "negar"
            rule_applied = "historical_chargeback"
        # 2. Verificar valor elevado e horário crítico
        elif check_high_value_and_time(transaction_amount, transaction_date):
            recommendation = "negar"
            rule_applied = "high_value_night"
        # 3. Verificar frequência de transações por dispositivo
        elif check_frequency_and_value(conn, device_id, transaction_date):
            recommendation = "negar"
            rule_applied = "frequency_value"
        else:
            # Aprovação padrão
            recommendation = "aprovar"
            rule_applied = "default"

        # Salvar a transação no log
        save_transaction_log(conn, data, recommendation, rule_applied, has_chargeback)

        # Retornar a decisão
        response = {
            "transaction_id": data.get("transaction_id"),
            "recomendação": recommendation  # Mantém a resposta com acento
        }
        return jsonify(response)

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao processar transação: {e}")
        return jsonify({"error": "Erro interno ao processar transação"}), 500
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == '__main__':
    # Executar a aplicação com um servidor de produção (Gunicorn recomendado)
    app.run(host='0.0.0.0', port=5000, debug=False)
