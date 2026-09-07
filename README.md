This project provides a robust pipeline for evaluating Large Language Model (LLM) outputs using the Deepeval framework.

It supports both OpenAI (for high-accuracy judging) and Ollama (for 100% local, private evaluation).

## Features

Dual Mode: Switch between OpenAI (GPT-4o) and Local (Qwen 2.5) with a single toggle.

Metrics: HallucinationMetric,AnswerRelevancyMetric,ToxicityMetric,BiasMetric.

Local Priority: Optimized for qwen2.5:3b via Ollama to run on standard hardware.

Async Implementation: Uses asynchronous clients for better performance.

## Prerequisites

Python 3.10 - 3.13 (Note: Python 3.14+ currently has Pydantic compatibility issues).

Ollama (for local evaluation).

OpenAI API Key (for cloud evaluation).

## Installation
1.Clone the repository:

git clone https://github.com/craitose/LLM-Evaluation-DEEPEVAL.git

cd DEEPEVAL

2.Install dependencies:

pip install -r requirements.txt

3.Set up environment variables:

Create a .env file in the root directory:

OPENAI_API_KEY=sk-your-actual-key-here

4.Pull the local models (if using Local Mode):

ollama pull llama3.2:latest (or any model your pc can handle)

ollama pull qwen2.5:3b (or any model your machine can handle)


## Usage

1.Configure Mode: Open test_complete.py and set MODE = 'local' or MODE = 'openai'.

2.Generate adverse inputs:

python generate_adverse_data.py

3.Run the script:

deepeval test run test_complete.py

4.View Results: 

python generate_report.py

deepeval_report.html will be available in root