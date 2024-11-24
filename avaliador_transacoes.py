import requests
import pandas as pd
from sqlalchemy import create_engine, text, Column, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
import concurrent.futures
import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

# Definir a base para o ORM
Base = declarative_base()

# Definir a classe do modelo para facilitar inserções em lote
class TransactionsApiResults(Base):
    __tablename__ = 'transactions_api_results'
    transaction_id = Column(Text, primary_key=True)
    has_cbk = Column(Boolean)
    recommendation = Column(Text)
    rule_applied = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

# Criar engine com pool de conexões usando as variáveis de ambiente
engine = create_engine(
    f"postgresql+psycopg2://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@"
    f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}",
    pool_size=20,
    max_overflow=0
)

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

# Função para processar uma única transação
def process_transaction(row):
    # Construir o payload
    payload = {
        "transaction_id": int(row['transaction_id']),
        "merchant_id": int(row['merchant_id']),
        "user_id": int(row['user_id']),
        "card_number": str(row['card_number']),
        "transaction_date": row['transaction_date'].isoformat() if row['transaction_date'] else None,
        "transaction_amount": float(row['transaction_amount']) if not pd.isnull(row['transaction_amount']) else 0,
        "device_id": int(row['device_id']) if row['device_id'] and not pd.isnull(row['device_id']) else None
    }

    try:
        # Enviar para a API
        response = requests.post("http://localhost:5000/evaluate_transaction", json=payload)
        # print(f"Enviando payload: {payload}")  # Comentado para reduzir a saída
        response.raise_for_status()  # Lança exceção para status HTTP de erro

        api_result = response.json()

        # Retornar os resultados
        return {
            "transaction_id": str(row['transaction_id']),
            "has_cbk": row['has_cbk'],
            "recommendation": api_result['recommendation'],
            "created_at": datetime.now(timezone.utc)
        }

    except requests.exceptions.RequestException as e:
        print(f"Erro de comunicação com a API: {e}")
        return None
    except Exception as e:
        print(f"Erro ao processar a transação {row['transaction_id']}: {e}")
        return None

# Função para processar todas as transações
def process_transactions(df_transactions):
    results = []
    results_to_insert = []
    batch_size = 100  # Defina o tamanho do lote

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_row = {executor.submit(process_transaction, row): row for _, row in df_transactions.iterrows()}
        total_transactions = len(df_transactions)
        for idx, future in enumerate(concurrent.futures.as_completed(future_to_row), 1):
            result = future.result()
            if result:
                results.append({
                    "transaction_id": result["transaction_id"],
                    "has_cbk": result["has_cbk"],
                    "recommendation": result["recommendation"]
                })
                results_to_insert.append(result)

                # Inserir em lotes
                if len(results_to_insert) >= batch_size:
                    try:
                        session.bulk_insert_mappings(TransactionsApiResults, results_to_insert)
                        session.commit()
                        results_to_insert.clear()
                        print(f"Inserido lote de {batch_size} registros no banco de dados.")
                    except Exception as e:
                        print(f"Erro ao inserir registros no banco: {e}")
                        session.rollback()

            # Opcional: Mostrar progresso
            if idx % 25 == 0:
                print(f"Processadas {idx}/{total_transactions} transações.")

    # Inserir quaisquer registros restantes
    if results_to_insert:
        try:
            session.bulk_insert_mappings(TransactionsApiResults, results_to_insert)
            session.commit()
            print(f"Inserido lote final de {len(results_to_insert)} registros no banco de dados.")
        except Exception as e:
            print(f"Erro ao inserir registros no banco: {e}")
            session.rollback()

    print("Transações processadas e salvas no banco com sucesso.")
    return results

# Consulta para extrair as transações
query = """
    SELECT transaction_id, merchant_id, user_id, card_number,
           transaction_date, transaction_amount, device_id, has_cbk
    FROM transactions;
"""

try:
    # Ler os dados e substituir NaN por None
    df_transactions = pd.read_sql_query(query, engine)
    df_transactions = df_transactions.where(pd.notnull(df_transactions), None)

    # Processar as transações
    results = process_transactions(df_transactions)

    # Calcular acurácia
    if len(results) > 0:
        df_results = pd.DataFrame(results)
        df_results['expected_recommendation'] = df_results['has_cbk'].apply(lambda x: "deny" if x else "approve")
        accuracy = (df_results['recommendation'] == df_results['expected_recommendation']).mean()
        print(f"Acurácia da API: {accuracy:.2%}")
    else:
        print("Nenhuma transação processada. Não é possível calcular a acurácia.")
finally:
    session.close()
    engine.dispose()
