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
├── notebooks/                            # Jupyter notebooks (run independently)
│   ├── 02-data-visualization.ipynb       #   EDA — hourly, daily, weekly, monthly seasonality
│   ├── 03-cross-year-comparison.ipynb    #   Cross-year comparison (2015/2018/2020), ensembles
│   ├── 04-results.ipynb                  #   Scatter plots — predicted vs actual
│   ├── 05-per-line-models.ipynb          #   Per-line models (10+ algorithms)
│   ├── 06-per-line-models-cyclical.ipynb #   Same with sin/cos cyclical features
│   ├── 01-data-processing.ipynb          #   Data pipeline reference (needs raw data)
│   └── experimental/                     #   Neural network experiments (need TensorFlow)
│
├── src/fortaleza_bus_forecast/           # Reusable Python package
│   ├── config.py                         #   Feature lists, constants, paths
│   ├── data/                             #   Data loading, holidays, preprocessing
│   ├── models/                           #   Model training, evaluation, metrics
│   └── visualization/                    #   Plotting functions
│
├── scripts/                              # Data pipeline utilities
│   ├── data_builder.py                   #   Raw CSV → hourly aggregation per line
│   ├── zero_filler.py                    #   Fill missing (line, hour) with 0
│   └── helper-funs.py                    #   Shared utils: metrics, week_of_month()
│
├── model-data/                           # Datasets (extract with `make data`)
├── performances/                         # Model performance CSVs
├── predict-vs-real/                      # Prediction output CSVs
├── images/                               # Generated plots (PDFs, PNGs)
├── feedback/                             # Improvement notes and analysis
├── Makefile                              # `make data` / `make clean-data`
└── pyproject.toml                        # Package config
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Jupyter Notebook or JupyterLab

### Installation

```bash
git clone https://github.com/medeirosvictor/fortaleza-bus-forecast.git
cd fortaleza-bus-forecast
pip install -e ".[full]"   # Installs package + xgboost, lightgbm, shap
make data                  # Extract model-ready datasets
```

### Running the Notebooks

All notebooks live in `notebooks/` and can be run **independently** — no ordering required:

| Notebook | What it does |
|----------|-------------|
| **`02-data-visualization`** | EDA — seasonality patterns by hour, day, week, month |
| **`05-per-line-models`** | Train & evaluate 10+ models per bus line |
| **`04-results`** | Scatter plots of predicted vs actual boarding counts |
| **`03-cross-year-comparison`** | Train on one year, predict another — generalization analysis |
| **`06-per-line-models-cyclical`** | Same as 05 but with sin/cos cyclical feature encoding |
| `01-data-processing` | *Reference only* — shows how raw data was processed (needs raw CSVs) |

## 🔬 Methodology

### Data

| Year | Period | Rows | Notes |
|------|--------|------|-------|
| 2015 | Jan – Dec | 795K | Full year |
| 2018 | Jan – Jul | 410K | Only 7 months available from ETUFOR |
| 2020 | Mar – Dec | 632K | No Jan/Feb; COVID-19 impact from March onward |

- **Source:** ETUFOR (Empresa de Transporte Urbano de Fortaleza) — electronic fare validation (smart card taps)
- **Scope:** Top 100 bus lines by ridership volume
- **Granularity:** Hourly passenger counts per bus line

### Feature Engineering

| Feature | Description |
|---------|-------------|
| `hour`, `hour_sin`, `hour_cos` | Hour of day + cyclical encoding |
| `day_of_week` + one-hot columns | Day of week (Monday=0 … Sunday=6) |
| `day_of_month`, `day_of_year` | Calendar position |
| `month`, `week_of_month` | Monthly/weekly position |
| `holiday`, `holiday_eve` | Brazilian national + Ceará/Fortaleza local holidays |

**Key insight:** Cyclical encoding (sin/cos) of temporal features preserves circular continuity — hour 23 is close to hour 0, December is close to January.

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

## 📦 Python Package

The project includes a reusable package at `src/fortaleza_bus_forecast/`:

```python
from fortaleza_bus_forecast.data import load_year_data, get_holidays
from fortaleza_bus_forecast.models import build_model_suite, train_and_evaluate
from fortaleza_bus_forecast.visualization import plot_predictions_vs_actual

# Load and explore
df = load_year_data(2015)            # 795K rows, 100 bus lines
line41 = load_line_data(2015, 41)    # Single line
```

## ⚠️ Notes

- **2020 includes COVID-19** — ridership dropped dramatically. Cross-year comparisons involving 2020 should be interpreted with this context.
- **Zero-filling:** Hours with no validations are filled with 0-count rows, distinguishing "no passengers" from "missing data."
- **Raw data** is not in the repo. Pre-processed datasets ship as `model-data/data.zip` (15 MB, extracted via `make data`).

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

*Exemplo: Linha 41 (2015) — uma das mais movimentadas de Fortaleza.*

### 🔬 Dados

| Ano | Período | Linhas | Observações |
|-----|---------|--------|------------|
| 2015 | Jan – Dez | 795 mil linhas | Ano completo |
| 2018 | Jan – Jul | 410 mil linhas | Apenas 7 meses disponíveis |
| 2020 | Mar – Dez | 632 mil linhas | Sem Jan/Fev; impacto da COVID-19 |

- **Fonte:** ETUFOR (Empresa de Transporte Urbano de Fortaleza)
- **Escopo:** Top 100 linhas de ônibus por volume de passageiros
- **Granularidade:** Contagem horária de passageiros por linha

### Engenharia de Features

| Feature | Descrição |
|---------|-----------|
| `hora`, `hour_sin`, `hour_cos` | Hora do dia + codificação cíclica |
| `d_semana` + colunas one-hot | Dia da semana (Segunda=0 … Domingo=6) |
| `d_mes`, `d_ano` | Posição no calendário |
| `mes`, `semana_do_mes` | Posição mensal/semanal |
| `feriado`, `vespera_feriado` | Feriados nacionais + locais de Fortaleza/Ceará |

**Insight principal:** A codificação cíclica (sin/cos) preserva a continuidade circular — a hora 23 fica próxima da hora 0, dezembro fica próximo de janeiro.

### Modelos Comparados

| Modelo | Biblioteca |
|--------|------------|
| Regressão Linear | scikit-learn |
| Regressão Ridge | scikit-learn |
| SVR | scikit-learn |
| Árvore de Decisão | scikit-learn |
| Random Forest | scikit-learn |
| Bagging (Árvore de Decisão) | scikit-learn |
| Gradient Boosting | scikit-learn |
| XGBoost | xgboost |
| LightGBM | lightgbm |
| **Stacking Ensemble** (XGBoost) | scikit-learn |

### 🚀 Como Executar

```bash
git clone https://github.com/medeirosvictor/fortaleza-bus-forecast.git
cd fortaleza-bus-forecast
pip install -e ".[full]"   # Instala o pacote + xgboost, lightgbm, shap
make data                  # Extrai os datasets
```

Todos os notebooks estão em `notebooks/` e podem ser executados independentemente.

| Notebook | O que faz |
|----------|-----------|
| **`02-data-visualization`** | EDA — padrões de sazonalidade |
| **`05-per-line-models`** | Treino e avaliação de 10+ modelos por linha |
| **`04-results`** | Scatter plots — predição vs real |
| **`03-cross-year-comparison`** | Generalização entre anos |
| **`06-per-line-models-cyclical`** | Variante com features cíclicas (sin/cos) |

### Orientação

- **Universidade:** Universidade de Fortaleza (UNIFOR) — Centro de Ciências Tecnológicas, Ciência da Computação
- **Orientador:** Prof. Dr. Carlos Caminha
- **Dados:** ETUFOR (Empresa de Transporte Urbano de Fortaleza)

---

## 📝 License

This project was developed as an undergraduate thesis at the University of Fortaleza (UNIFOR). Data is sourced from Fortaleza's public transit authority (ETUFOR).

## 🤝 Acknowledgments

- **ETUFOR** (Empresa de Transporte Urbano de Fortaleza) for the fare validation data
- **Prof. Dr. Carlos Caminha** — thesis advisor
- University of Fortaleza (UNIFOR) — Centro de Ciências Tecnológicas, Computer Science
