# Smart Business Analyst

Smart Business Analyst is an AI-powered business analysis assistant that allows users to ask questions about sales data using natural language.

The system analyzes business data from a Supermart sales dataset and provides useful business insights through an AI agent.

## Features

- Total revenue analysis
- Monthly sales analysis
- Top products analysis
- Customer statistics
- Comparison between different periods
- Natural language question answering
- Automatic tool selection
- Data visualization
- Error handling and invalid question handling
- Interactive Gradio interface

## Technologies Used

- Python
- Pandas
- Matplotlib
- Gradio
- Ollama
- Large Language Model (LLM)

## Project Structure

text
Smart Business Analysis/
│
├── agent.py
├── app.py
├── tools.py
├── llm.py
├── business_analysis.py
├── requirements.txt
├── README.md
│
└── data/
    └── supermart.csv


## How the System Works

The user enters a business question in natural language.

The AI agent analyzes the question and determines which business analysis tool should be used.

The selected tool processes the sales data and returns the required result.

The result is then interpreted and presented to the user.

For supported questions, the system can also generate a suitable visualization.

## Available Analysis Tools

### 1. Total Revenue

Calculates the total sales revenue from the dataset.

Example:

text
What is the total revenue?


### 2. Monthly Sales

Analyzes sales across different months.

Example:

text
Show monthly sales


### 3. Top Products

Finds the products or sub-categories with the highest sales.

Example:

text
What are the top products?


### 4. Customer Statistics

Provides statistics about customers and their sales.

Example:

text
Who are the top customers?


### 5. Period Comparison

Compares sales between two different periods.

Example:

text
Compare Q1 2018 with Q2 2018


## Visualizations

The system supports different visualizations depending on the question.

Examples include:

* Bar charts for top products
* Line charts for monthly sales
* Bar charts for period comparisons

## Running the Project

First, install the required Python packages:

bash
pip install -r requirements.txt


Then run the Gradio application:

bash
python app.py


The application will open a local web interface where users can interact with the AI business analyst.

## Example Questions

text
What is the total revenue?

What are the top products?

Show monthly sales

Who are the top customers?

Compare Q1 2018 with Q2 2018


## Error Handling

The system is designed to handle invalid or unsupported questions gracefully.

For example, if the user enters a question that the agent cannot understand, the system returns a friendly message asking the user to provide a business-related question.

## Future Improvements

Possible future improvements include:

* More business analysis tools
* More advanced visualizations
* Automatic report generation
* Dashboard integration
* More datasets
* Advanced business recommendations
* Improved natural language understanding
* Deployment as a web application

## Author

Smart Business Analysis Project



