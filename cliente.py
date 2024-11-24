# Este script permitirá que você defina os parâmetros de uma transação individual e envie uma requisição para a API para avaliação.

import requests
import json

# Defina os parâmetros da transação
transaction_data = {
    "transaction_id": 2342357,
    "merchant_id": 56107,
    "user_id": 97051,
    "card_number": "434505******9116",
    "transaction_date": "2019-11-30T23:16:32.812632",
    "transaction_amount": 5000,
    "device_id": 285475
}

# URL da API
api_url = "http://localhost:5000/evaluate_transaction"

try:
    # Enviar a requisição POST para a API
    response = requests.post(api_url, json=transaction_data)
    response.raise_for_status()  # Lança uma exceção para códigos de status 4xx ou 5xx

    # Exibir a resposta da API
    api_response = response.json()
    print("Resposta da API:")
    print(json.dumps(api_response, indent=4, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"Erro ao se comunicar com a API: {e}")
except Exception as e:
    print(f"Erro: {e}")
