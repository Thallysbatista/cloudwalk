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
- **`app_api_transacoes_unitarias.py`**: API antifraude implementada em Flask que avalia transações unitárias.
- **`avaliador_transacoes.py`**: Script que processa transações em lote e envia os dados para a API para avaliação.
- **`cliente.py`**: Script cliente que envia transações individuais para a API para avaliação.

---

#### Tecnologias Utilizadas

1. Banco de Dados PostgreSQL:
   * Hospedado no AWS RDS.
   * Contém as tabelas ``transactions``, ``transactions_log`` e ``transactions_api_results``.

2. Metabase:
   * Instanciado no AWS EC2.
   * Conectado ao banco de dados para criar dashboards e executar análises SQL.

3. Python:
   * Análise exploratória, criação da API, e automação de testes.

4. Flask:
   * Framework utilizado para a implementação da API.

5. SQLAlchemy:
   * Gerenciamento de conexões e consultas ao banco de dados.

---

#### Banco de Dados

- Estrutura das Tabelas
1. Tabela ``transactions``: Contém os dados transacionais originais.

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

2. Tabela ``transactions_log``: Armazena todas as transações avaliadas pela API, com as regras aplicadas e a decisão final.

```sql
CREATE TABLE transactions_log (
    transaction_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    merchant_id BIGINT,
    card_number VARCHAR(16),
    transaction_date TIMESTAMP,
    transaction_amount DOUBLE PRECISION,
    device_id BIGINT,
    recommendation VARCHAR(20),
    rule_applied VARCHAR(50),
    has_chargeback BOOLEAN
);
```

3. Tabela ``transactions_api_results``: Salva os resultados de testes realizados pela API para validação posterior.

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
  - `Flask`
  - `psycopg2`
  - `requests`
  - `concurrent.futures`  
  - `python-dotenv` (para carregar variáveis de ambiente do arquivo `.env`)
- **Ambiente Virtual**:
   - Recomendado para isolar as dependências do projeto.

---

#### Configuração do Ambiente Virtual

1. **Criar o Ambiente Virtual**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

2. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

---

#### Instalação e Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/Thallysbatista/cloudwalk.git
   cd cloudwalk-test
   ```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```env
   DB_HOST=url_host
   DB_NAME=nome_do_Banco_de_dados
   DB_USER=usuario
   DB_PASSWORD=senha_banco_de_dados
   DB_PORT=5432
   ```

---

#### Como rodar o projeto

1.  **Execute os scripts SQL para criar as tabelas.**

2. **Iniciar o servidor da API**
   ```bash
   python app_api_transacoes_unitarias.py
   ```

3. **Processar transações em lote e inserir no banco**
   ```bash
   python avaliador_transacoes.py
   ```

4. **Enviar transação individual para a API**
   ```bash
   python cliente.py
   ```

5. **Análise no Metabase:**
   [Link para dashboard](http://18.117.137.2:3000/public/dashboard/461921e1-81d7-47ca-9abf-5e59f38400fb)

---

#### Testes e Validação

1. **Testes Automáticos em Lote:**
   - O script ``avaliador_transacoes.py`` processa dados existentes da tabela transactions e os envia para a API.
   - Resultados são salvos na tabela ``transactions_api_results`` para comparação futura.

2. **Testes Unitários com Transações Individuais:**
   - O script ``cliente.py`` permite enviar transações individuais para serem avaliadas pela API.
   - Isso facilita a validação de cenários específicos.

3. **Acurácia:**
   - A eficácia da API é avaliada comparando o status real de chargebacks ``(has_cbk)`` com a recomendação da API ``(recommendation)``.

---

#### API Antifraude

A API foi projetada para receber informações de transações, avaliar com base em regras predefinidas, e retornar uma recomendação para "aprovar" ou "negar".

- **Regras Implementadas**

1. **Histórico de Chargebacks:**
   - Negar transações de usuários, comerciantes ou cartões com histórico de chargebacks.

2. **Valor Elevado e Horários Críticos:**
   - Negar transações acima de R$ 1800 realizadas entre 20h e 4h.

3. **Frequência de Transações:**
   - Negar transações de dispositivos que realizaram mais de 3 transações em 1 hora, e cujo valor total ultrapasse R$ 2500.

4. **Aprovação Padrão:**
   - Transações que não atendem aos critérios acima são aprovadas.

---

#### Exemplo de Payload

- **Entrada**:

```json
{
   "transaction_id": 21320398,
   "merchant_id": 29744,
   "user_id": 97051,
   "card_number": "434505******9116",
   "transaction_date": "2019-12-01T23:16:32.812632",
   "transaction_amount": 374.56,
   "device_id": 285475
}
```

- **Saída**:

```json
{
   "transaction_id": 21320398,
   "recommendation": "approve"
}
```

---

#### Considerações Finais

Este projeto visa demonstrar a capacidade de implementar uma solução para detecção de fraudes em transações financeiras, utilizando Python, Flask e PostgreSQL. A API antifraude foi desenvolvida para ser escalável, eficiente e facilmente ajustável a novas regras de negócio. Além disso, a integração com o Metabase facilita a análise dos resultados e a geração de insights para tomadas de decisão.

Caso queira contribuir ou realizar melhorias, sinta-se à vontade para abrir uma issue ou um pull request no repositório do GitHub.

