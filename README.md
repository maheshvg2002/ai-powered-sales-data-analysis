# AI Powered Sales Data Analysis

An AI-powered Streamlit application that enables interactive sales data analysis using voice commands, visual analytics, and Azure OpenAI–driven insights. Designed for business users and analysts to quickly extract actionable intelligence from structured sales data.

---

## Key Features

- Upload sales data (CSV or Excel)
- Automatic data preprocessing and preview
- Voice-based data querying using speech recognition
- AI-generated statistical insights powered by Azure OpenAI
- Interactive visualizations:
  - Scatter plots
  - Bar charts
  - Pie charts
- Downloadable insight reports (text format)
- Business-focused insights and recommendations
- Modern Streamlit UI with responsive layout

---

## Tech Stack

- **Frontend / UI:** Streamlit
- **Data Processing:** Pandas
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Voice Input:** SpeechRecognition
- **LLM:** Azure OpenAI (GPT-4o)
- **Language:** Python 3

---

## Project Structure

│
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── .gitignore

--- 


---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/sales-data-analysis-ai.git
cd ai-powered-sales-data-analysis

---

Install Dependencies

- pip install -r requirements.txt

---

Azure OpenAI Configuration

This application uses Streamlit Secrets for secure credential management.

Create a file at:

.streamlit/secrets.toml


Add the following:

AZURE_ENDPOINT = "https://<your-resource-name>.openai.azure.com/"
AZURE_API = "<your-azure-openai-api-key>"
API_VERSION = "2024-02-15-preview"

---

Running the Application

- streamlit run sales_data_analysis.py
