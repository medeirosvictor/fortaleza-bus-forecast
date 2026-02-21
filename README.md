# 🚌 Passenger Boarding Prediction for Fortaleza's Bus Transit System

> **Undergraduate Thesis (TCC)** — Predicting hourly passenger boarding counts on Fortaleza's public bus system using machine learning.

Fortaleza is the capital of Ceará, Brazil, with a bus network serving millions of monthly rides. This project uses **fare validation data** (smart card taps) to train per-line ML models that predict how many passengers will board a given bus line in a given hour — useful for fleet allocation, route planning, and schedule optimization.

## 📊 Key Results

Best-performing models achieve **R² > 0.95** on high-traffic bus lines, accurately capturing hourly and weekly seasonality patterns.

| Model | R² | RMSE | MAE |
|-------|-----|------|-----|
| Stacking Ensemble (XGBoost meta) | **0.958** | 90.6 | 60.2 |
| Gradient Boosting | 0.957 | 91.5 | 58.9 |
| Random Forest (tuned) | 0.937 | 111.2 | 70.0 |
| Bagging (Decision Tree) | 0.936 | 111.4 | 71.3 |
| Random Forest (default) | 0.920 | 125.2 | 68.7 |
| XGBoost | 0.910 | 132.7 | 74.2 |
| Ridge Regression | 0.882 | 151.8 | 83.1 |
| SVR | −0.001 | 441.4 | 354.3 |

*Example: Bus line 41 (2015) — one of Fortaleza's busiest routes. Trained on 80% of the year, tested on 20%.*

### Hourly Seasonality Pattern

![Hourly seasonality — average passenger boardings by hour of day](images/sazonalidade-hora.png)

*Clear bimodal pattern: morning rush (~6–7 AM) and evening rush (~17–18 PM), with a midday plateau.*

## 🏗️ Project Structure

```
├── notebooks/
│   ├── 01-data-processing.ipynb          # Data wrangling pipeline (reference — needs raw data)
│   ├── 02-data-visualization.ipynb       # EDA — hourly, daily, weekly, monthly seasonality
│   ├── 03-cross-year-comparison.ipynb    # Cross-year comparison (2015/2018/2020), ensemble models
│   ├── 04-results.ipynb                  # Aggregated results, scatter plots (predicted vs actual)
│   ├── 05-per-line-models.ipynb          # Per-line models (all algorithms)
│   ├── 06-per-line-models-cyclical.ipynb # Same with sin/cos cyclical feature encoding
│   └── experimental/                     # Neural network experiments (need TensorFlow)
│
├── src/fortaleza_bus_forecast/           # Reusable Python package
│   ├── config.py                         # Feature lists, constants, paths
│   ├── data/                             # Data loading, holidays, preprocessing
│   ├── models/                           # Model training, evaluation, metrics
│   └── visualization/                    # Thesis-quality plotting functions
│
├── scripts/                              # Data pipeline scripts
│   ├── data_builder.py                   # Raw CSV → aggregated hourly validations per line
│   ├── zero_filler.py                    # Fills missing (line, hour) combos with 0
│   └── helper-funs.py                    # Shared utilities: metrics, week_of_month()
│
├── model-data/                           # Pre-processed CSVs (extract with `make data`)
├── performances/                         # Model performance CSVs (per line, per config)
├── predict-vs-real/                      # Prediction output CSVs for plotting
├── images/                               # Generated visualizations (PDFs, PNGs)
└── Makefile                              # `make data` to extract datasets
```

## 🔬 Methodology

### Data

- **Source:** Fortaleza's electronic fare validation system (smart card tap data)
- **Years analyzed:** 2015, 2018, 2020
- **Scope:** Top 100 bus lines by ridership volume
- **Granularity:** Hourly passenger counts per bus line

### Feature Engineering

| Feature | Description |
|---------|-------------|
| `hour`, `hour_sin`, `hour_cos` | Hour of day + cyclical encoding |
| `day_of_week` + one-hot columns | Day of week (Sunday=0 … Saturday=6) |
| `day_of_month`, `day_of_year` | Calendar position |
| `month`, `week_of_month` | Monthly/weekly position |
| `holiday`, `holiday_eve` | Brazilian national + Ceará/Fortaleza local holidays |

**Key insight:** Cyclical encoding (sin/cos) of temporal features preserves the circular continuity that one-hot encoding destroys — hour 23 is close to hour 0, December is close to January.

### Models Compared

| Model | Library |
|-------|---------|
| Linear Regression | scikit-learn |
| Ridge Regression | scikit-learn |
| SVR (Support Vector Regression) | scikit-learn |
| Decision Tree Regressor | scikit-learn |
| Random Forest Regressor | scikit-learn |
| Bagging (Decision Tree base) | scikit-learn |
| Gradient Boosting | scikit-learn |
| XGBoost | xgboost |
| LightGBM | lightgbm |
| **Stacking Ensemble** (XGBoost meta-learner) | scikit-learn |

### Evaluation Metrics

- **R²** — Coefficient of determination
- **RMSE** — Root mean squared error
- **MAE** — Mean absolute error
- **MAPE** — Mean absolute percentage error

### Training Strategy

- **Per-line models:** Each of the top 100 bus lines gets its own trained model
- **Walk-forward experiments:** Train on N months, predict the next period (1–2 weeks ahead)
- **Cross-year comparison:** Models trained on 2015 data evaluated against 2018/2020 patterns

## ⚠️ Notes

- **2020 data includes the COVID-19 pandemic period**, which drastically reduced ridership. Cross-year comparisons involving 2020 should be interpreted with this context.
- **Zero-filling:** Hours with no recorded validations are explicitly filled with 0-count rows, distinguishing "no passengers" from "missing data."
- Raw data files are not included in the repository (gitignored). The pre-processed model-ready CSVs are available in `model-data/`.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Jupyter Notebook or JupyterLab

### Installation

```bash
git clone https://github.com/medeirosvictor/fortaleza-bus-forecast.git
cd fortaleza-bus-forecast
pip install -e ".[full]"   # Installs package + xgboost, lightgbm, shap
# or: pip install -r requirements.txt  (minimal deps only)

# Extract the model-ready datasets (required for notebooks)
make data
```

### Running

All notebooks are in the `notebooks/` folder and can be run independently:

1. **`02-data-visualization.ipynb`** — EDA and seasonality analysis
2. **`05-per-line-models.ipynb`** — Core modeling workflow (train & evaluate)
3. **`04-results.ipynb`** — Visualize predictions vs actual values
4. **`03-cross-year-comparison.ipynb`** — Cross-year generalization analysis
5. **`01-data-processing.ipynb`** — Data pipeline reference (needs raw data)

---

## 📦 Python Package

The project includes a reusable Python package at `src/fortaleza_bus_forecast/`:

```python
from fortaleza_bus_forecast.data import load_year_data, get_holidays
from fortaleza_bus_forecast.data.preprocessor import prepare_features
from fortaleza_bus_forecast.models import build_model_suite, train_and_evaluate
from fortaleza_bus_forecast.visualization import plot_predictions_vs_actual

# Load data
df = load_year_data(2015)

# Feature engineering
df = prepare_features(df, year=2015, cyclical=False)

# Build and train models
models = build_model_suite()
```

Install in development mode: `pip install -e ".[full]"`

---

## 🇧🇷 Sobre o Projeto (Português)

Este repositório contém o código e os dados processados do meu **Trabalho de Conclusão de Curso (TCC)** na Universidade de Fortaleza (UNIFOR):

> **Predição e Análise de Dados de Embarque de Passageiros no Sistema de Transporte Público por Ônibus de Fortaleza, Ceará**

### Resumo

O projeto utiliza dados do sistema de validação eletrônica de tarifas (dados de cartão) do transporte público de Fortaleza para treinar modelos de aprendizado de máquina que preveem a quantidade de passageiros embarcando por hora em cada linha de ônibus.

Foram analisados dados de três anos: **2015**, **2018** e **2020** — abrangendo as 100 linhas com maior volume de passageiros.

### 📊 Resultados Principais

Os melhores modelos alcançaram **R² > 0,95** nas linhas de maior movimento, capturando com precisão os padrões de sazonalidade horária e semanal.

| Modelo | R² | RMSE | MAE |
|--------|-----|------|-----|
| Stacking Ensemble (XGBoost meta) | **0,958** | 90,6 | 60,2 |
| Gradient Boosting | 0,957 | 91,5 | 58,9 |
| Random Forest (ajustado) | 0,937 | 111,2 | 70,0 |
| Bagging (Árvore de Decisão) | 0,936 | 111,4 | 71,3 |
| Random Forest (padrão) | 0,920 | 125,2 | 68,7 |
| XGBoost | 0,910 | 132,7 | 74,2 |
| Ridge Regression | 0,882 | 151,8 | 83,1 |
| SVR | −0,001 | 441,4 | 354,3 |

*Exemplo: Linha 41 (2015) — uma das mais movimentadas de Fortaleza. Treino em 80% do ano, teste em 20%.*

### 🔬 Metodologia

#### Dados

- **Fonte:** Sistema de validação eletrônica de tarifas (dados de cartão) de Fortaleza
- **Anos analisados:** 2015, 2018, 2020
- **Escopo:** Top 100 linhas de ônibus por volume de passageiros
- **Granularidade:** Contagem horária de passageiros por linha

#### Engenharia de Features

| Feature | Descrição |
|---------|-----------|
| `hora`, `hora_sin`, `hora_cos` | Hora do dia + codificação cíclica |
| `d_semana` + colunas one-hot | Dia da semana (Domingo=0 … Sábado=6) |
| `d_mes`, `d_ano` | Posição no calendário |
| `mes`, `semana_do_mes` | Posição mensal/semanal |
| `feriado`, `vespera_feriado` | Feriados nacionais + locais de Fortaleza/Ceará |

**Insight principal:** A codificação cíclica (sin/cos) das features temporais preserva a continuidade circular que o one-hot encoding destrói — a hora 23 fica próxima da hora 0, dezembro fica próximo de janeiro.

#### Modelos Comparados

| Modelo | Biblioteca |
|--------|------------|
| Regressão Linear | scikit-learn |
| Regressão Ridge | scikit-learn |
| SVR (Support Vector Regression) | scikit-learn |
| Árvore de Decisão | scikit-learn |
| Random Forest | scikit-learn |
| Bagging (base: Árvore de Decisão) | scikit-learn |
| Gradient Boosting | scikit-learn |
| XGBoost | xgboost |
| LightGBM | lightgbm |
| **Stacking Ensemble** (meta-learner: XGBoost) | scikit-learn |

#### Métricas de Avaliação

- **R²** — Coeficiente de determinação
- **RMSE** — Raiz do erro quadrático médio
- **MAE** — Erro absoluto médio
- **MAPE** — Erro percentual absoluto médio

#### Estratégia de Treinamento

- **Modelos por linha:** Cada uma das 100 linhas recebe seu próprio modelo treinado
- **Walk-forward:** Treina com N meses, prevê o próximo período (1–2 semanas à frente)
- **Comparação entre anos:** Modelos treinados em 2015 avaliados contra padrões de 2018/2020

### Principais Contribuições

- **Comparação de 10+ algoritmos de ML** (Regressão Linear, Ridge, SVR, Árvore de Decisão, Random Forest, Bagging, Gradient Boosting, XGBoost, LightGBM e Stacking Ensemble)
- **Engenharia de features temporais** com codificação cíclica (sin/cos) para hora, dia da semana, mês etc.
- **Flags de feriados** nacionais brasileiros e locais de Fortaleza/Ceará
- **Estratégia de zero-fill** para distinguir "zero passageiros" de "dado ausente"
- **Análise comparativa entre anos**, incluindo o impacto da pandemia de COVID-19 nos dados de 2020
- **Modelos por linha** — cada uma das 100 linhas recebe seu próprio modelo treinado

### ⚠️ Observações

- **Os dados de 2020 incluem o período da pandemia de COVID-19**, que reduziu drasticamente o número de passageiros. Comparações entre anos envolvendo 2020 devem ser interpretadas com esse contexto.
- **Zero-fill:** Horas sem validações registradas são explicitamente preenchidas com linhas de contagem 0, distinguindo "sem passageiros" de "dado ausente."
- Os arquivos de dados brutos não estão incluídos no repositório (gitignored). Os CSVs pré-processados prontos para modelagem estão disponíveis em `model-data/`.

### 🚀 Como Executar

#### Pré-requisitos

- Python 3.10+
- Jupyter Notebook ou JupyterLab

#### Instalação

```bash
git clone https://github.com/medeirosvictor/fortaleza-bus-forecast.git
cd fortaleza-bus-forecast
pip install -e ".[full]"   # Instala o pacote + xgboost, lightgbm, shap

# Extrair os datasets prontos para modelagem (necessário para os notebooks)
make data
```

#### Execução

Todos os notebooks estão na pasta `notebooks/` e podem ser executados independentemente:

1. **`02-data-visualization.ipynb`** — EDA e análise de sazonalidade
2. **`05-per-line-models.ipynb`** — Fluxo principal de modelagem (treino e avaliação)
3. **`04-results.ipynb`** — Visualização de predições vs valores reais
4. **`03-cross-year-comparison.ipynb`** — Análise de generalização entre anos
5. **`01-data-processing.ipynb`** — Referência do pipeline de dados (precisa dos dados brutos)

### Orientação

- **Universidade:** Universidade de Fortaleza (UNIFOR) — Centro de Ciências Tecnológicas, Curso de Ciência da Computação
- **Dados:** ETUFOR (Empresa de Transporte Urbano de Fortaleza)

---

## 📝 License

This project was developed as an undergraduate thesis at the University of Fortaleza (UNIFOR). Data is sourced from Fortaleza's public transit authority (ETUFOR).

## 🤝 Acknowledgments

- **ETUFOR** (Empresa de Transporte Urbano de Fortaleza) for the fare validation data
- University of Fortaleza (UNIFOR) — Centro de Ciências Tecnológicas, Computer Science
