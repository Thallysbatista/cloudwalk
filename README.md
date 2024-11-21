# Cloudwalk

## Software Engineer Test

### Transactional Sample Case

#### Descrição

Este projeto aborda o case fornecido no [link](https://gist.github.com/cloudwalk-tests/76993838e65d7e0f988f40f1b1909c97#file-transactional-sample-csv).  
O objetivo é analisar e processar os dados transacionais de forma eficiente, extraindo insights relevantes e demonstrando habilidades em manipulação de dados e banco de dados.

---

#### Estrutura do Repositório

- **`transactional_sample.csv`**: Arquivo de dados fornecido para o case.
- **`script.ipynb`**: Script Python no formato Jupyter Notebook que:
  1. Carrega os dados do CSV em um DataFrame.
  2. Realiza transformações e análises básicas.
  3. Insere os dados processados em um banco de dados PostgreSQL.
- **`README.md`**: Instruções e informações detalhadas sobre o projeto.

---

#### Pré-Requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- **Python 3.8+**: Para rodar o script.
- **PostgreSQL**: Para armazenar os dados processados.
- **Bibliotecas Python**:
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `sqlalchemy`
  - `sklearn.preprocessing`
- **Ambiente Virtual**:
   - Recomendado para isolar as dependências do projeto.

---

#### Configuração do Ambiente Virtual

1. **Criar o Ambiente Virtual**:
   ```bash
   python -m venv venv

---
#### Instalação e Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/Thallysbatista/cloudwalk.git
   cd cloudwalk-test


#### Estrutura da Tabela no PostgreSQL `transactions`

```sql
CREATE TABLE transactions (
    transaction_id BIGINT,
    merchant_id BIGINT,
    user_id BIGINT,
    card_number VARCHAR(16),
    transaction_date TIMESTAMP,
    transaction_amount DOUBLE PRECISION,
    device_id DOUBLE PRECISION,
    has_cbk BOOLEAN
);


A tabela `transactions` armazena informações sobre transações financeiras, como IDs de usuário e comerciante, valores de transação, e dados do dispositivo usado para a transação. O campo `has_cbk` indica se houve chargeback.
