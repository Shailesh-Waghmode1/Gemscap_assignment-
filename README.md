# 📊 Gemscap – Quant Developer Evaluation Assignment

## Overview

This project is a **real-time quantitative analytics dashboard** developed as part of the **Gemscap Quant Developer Evaluation Assignment**.

The application demonstrates an **end-to-end analytical workflow**, covering:
- Live market data ingestion
- Persistent storage and resampling
- Quantitative analytics
- Interactive visualization
- Alerts and data export

The system is intentionally designed as a **local, modular prototype** that reflects how a scalable real-time analytics stack could evolve in a production trading or research environment.

---

## Project Architecture

The system follows a **layered architecture** with clear separation of concerns, enabling maintainability and extensibility.

### Architecture Diagram
   
   ![Architecture Diagram](projectarchitecture.png)

### Data Flow

The application implements a **unidirectional data flow** from ingestion to visualization:

1. **External Data Source**
   - Live market data streamed from Binance Futures WebSocket API
   - Real-time tick data for multiple symbols

2. **Data Ingestion Layer** (`ingestion.py`)
   - Asynchronous WebSocket connections using `asyncio` and `websockets`
   - Captures: timestamp, symbol, price, quantity
   - Non-blocking concurrent processing for multiple streams

3. **Storage Layer** (`storage.py`)
   - Persistent storage using SQLite
   - Efficient tick-level data storage
   - Optimized for time-series queries

4. **Analytics Engine** (`analytics.py`)
   - On-demand resampling: 1s, 1m, 5m OHLC bars
   - Statistical computations:
     - OLS hedge ratio estimation
     - Spread calculation
     - Rolling Z-score
     - Rolling correlation
     - ADF (Augmented Dickey-Fuller) stationarity test
   - Powered by `pandas`, `numpy`, and `statsmodels`

5. **Frontend UI** (`app.py`)
   - Interactive Streamlit dashboard
   - Real-time chart updates
   - Configurable parameters (symbols, timeframes, thresholds)
   - Organized tabs: Prices, Analytics, Statistical Tests, Export
   - Z-score breach alerts

### Architectural Principles

- **Modularity**: Each layer has a single, well-defined responsibility
- **Loose Coupling**: Components communicate through clean interfaces
- **Extensibility**: New data sources or analytics can be added without refactoring
- **Separation of Concerns**: Business logic, data access, and presentation are isolated
- **Scalability Path**: Local prototype designed with production patterns in mind

---

## Key Features

### 🔹 Real-Time Data Ingestion
- Live tick data streamed from **Binance Futures WebSocket**
- Captured fields:
  - `timestamp`
  - `symbol`
  - `price`
  - `quantity`
- Supports multiple symbols simultaneously

### 🔹 Storage & Resampling
- Raw tick data stored in **SQLite**
- On-the-fly resampling into:
  - **1 second**
  - **1 minute**
  - **5 minute** bars
- No analytics require more than **one day of historical data**

### 🔹 Quantitative Analytics
- Multi-symbol price visualization
- **OLS hedge ratio estimation**
- **Spread calculation**
- **Rolling Z-score**
- **Rolling correlation**
- **ADF (Augmented Dickey-Fuller) test**
- Visual alert when Z-score threshold is breached

### 🔹 Interactive Frontend
- Built using **Streamlit**
- User controls:
  - Symbol selection
  - Timeframe selection
  - Rolling window size
  - Z-score alert threshold
- Organized into tabs:
  - Prices
  - Analytics
  - Statistical Tests
  - Data Export
- Light / Dark mode toggle

### 🔹 Alerts
- Real-time **Z-score threshold alert**
- Clearly highlighted to assist quick decision-making

### 🔹 Data Export
- Download resampled OHLC data as **CSV**
- Enables offline analysis and reproducibility

---

## Technology Stack

### Backend & Analytics
- Python 3
- asyncio
- websockets
- pandas
- numpy
- statsmodels
- SQLite

### Frontend
- Streamlit

---

## Folder Structure

```
gemscap-quant-dashboard/
│
├── ScreenShots/
│   ├── adf.png
│   ├── z_score_calculation.png
│   ├── analytics.png
│   ├── correlation.png
│   ├── download_csv_file.png
│   └── live_price_data_table.png
│
├── app.py
├── analytics.py
├── ingestion.py
├── storage.py
├── README.md


```
## Setup & Installation


### 1️⃣ Clone the repository
```bash
git clone https://github.com/Shailesh-Waghmode1/Gemscap_assignment.git
cd GEMSCAP_ASSIGNMENT
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the application
```bash
streamlit run app.py
```

The dashboard will automatically open in your browser.

---

## Notes on Deployment

- The application is designed primarily for **local execution**
- Live WebSocket ingestion works reliably when run locally
- When deployed on **Streamlit Community Cloud**, WebSocket connections may be limited due to platform restrictions

This limitation does not affect the architectural intent or analytical demonstration of the assignment.

---

## ChatGPT Usage Transparency

ChatGPT was used as a development assistant for:
- Structuring the system architecture
- Debugging Streamlit UI behavior
- Improving code clarity and modularity
- Writing documentation

All design decisions, implementation logic, and final code integration were reviewed and implemented manually.

---

## Design Philosophy

- **Clarity over complexity** – readable and maintainable code
- **Modularity** – clean separation of concerns
- **Extensibility** – easy to add new analytics or data sources
- **Prototype mindset** – designed to scale conceptually without premature optimization

---

## Conclusion

This project demonstrates the ability to:
- Work with real-time financial data
- Apply statistical and quantitative techniques
- Design modular analytical systems
- Build intuitive, interactive dashboards
- Communicate design decisions clearly

The implementation focuses on business usefulness and analytical reasoning, aligning with the expectations of a quantitative trading and research environment.

---

## 📸 Application Screenshots

### 🔹 Live Price Data (Table View)
Shows real-time resampled price data in tabular form.

![Live Price Data Table](ScreenShots/live_price_data_table.png)

---

### 🔹 Analytics Dashboard
Displays spread, hedge ratio, and Z-score calculations.

![Analytics Dashboard](ScreenShots/analytics.png)

---


### 🔹 Rolling Correlation
Rolling correlation between selected instruments.

![Rolling Correlation](ScreenShots/correlation.png)

---

### 🔹 ADF Test on Spread
ADF test results indicating stationarity of the spread.

![ADF Test](ScreenShots/adf.png)

---

### 🔹 CSV Data Export
Download functionality for resampled OHLC and analytics data.

![CSV Export](ScreenShots/download_csv_file.png)
