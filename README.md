🏠 Autonomous Real Estate Analyst (Dallas Edition)
An intelligent, AI-powered agentic workflow that identifies undervalued real estate properties in Dallas. Built with n8n, OpenAI, and Python, this agent automates the search process and provides valuation estimates using a Machine Learning (Random Forest) model.

📂 Project Structure
This repository contains the following essential files:

docker-compose.yaml & dockerfile

Configuration files to set up the n8n environment with Python support.

Ensures that libraries like pandas, scikit-learn, and numpy are installed and available for the n8n python node.

AI Housing chatbot (1).json

The complete n8n workflow export.

Contains the AI Agent logic, Function Calling definitions, and flow control (Chat vs. Email triggers).

DallasHouseodel.py

The core Python script (Model).

Handles data loading, training the Random Forest Regressor, and executing the search and calculate tools invoked by the AI.

November_Zillow_Dallas_11-16-22.csv

The dataset used for training the model and searching for listings.

Contains historical real estate data for the Dallas area (Zillow).

n8n_data/

Directory for persistent n8n data storage.

🚀 Setup & Installation
1. Prerequisites
Docker & Docker Compose installed.

An OpenAI API Key.

A Google Cloud project (for Gmail API credentials).

2. Run the Environment
Use Docker Compose to build the custom n8n image with Python dependencies enabled:

Bash

docker-compose up -d --build
3. Import the Workflow
Open n8n (usually at http://localhost:5678).

Go to Workflows > Import.

Select AI Housing chatbot (1).json.

4. Configuration
Credentials: Set up your OpenAI and Gmail credentials in n8n.

File Paths: Ensure the DallasHouseodel.py script points to the correct location of the CSV file inside the Docker container (e.g., /files/November_Zillow_Dallas_11-16-22.csv).

🤖 Usage
Chat Mode (Interactive)
Trigger: Use the n8n Chat interface.

Example Prompt: "Find me the best investment deals in zip code 75201."

Output: The agent returns a Markdown formatted list of undervalued properties directly in the chat.

Email Mode (Scheduled)
Trigger: Runs automatically via the Schedule Trigger (e.g., daily at 07:00 AM) OR by sending the prompt AUTO_DAILY_REPORT.

Output: The agent generates a comprehensive report and emails it via Gmail .

🧠 How It Works
Intent Recognition: The AI Agent determines if it needs to search for data or calculate a specific home value.

Tool Execution: It calls the Python script (DallasHouseodel.py) to run the Machine Learning model on the CSV data.

Result Parsing: The Python script returns JSON data (stats, listings, or valuation).

Response: The AI formats the data into a readable summary or an HTML email.
