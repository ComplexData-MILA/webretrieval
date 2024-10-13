# Web Retrieval Agents for Evidence-Based Misinformation Detection

This repository contains the Python script for a two-agent search system designed to detect misinformation based on evidence. The approach leverages web retrieval agents to verify facts against trusted sources. For an in-depth explanation of the methodology and system architecture, please refer to our paper: [Web Retrieval Agents for Evidence-Based Misinformation Detection](https://arxiv.org/abs/2409.00009).

## Prerequisites
This project takes a JSON file as input and verifies all facts in parallel using a search engine and the ChatGPT API. Refer to the fact.json file in the verifact directory for the format of the JSON file.

Before running the script, ensure that all necessary Python packages are installed. You can install these packages using pip:

```bash
pip install -r requirements.txt
```
Ensure you have a valid OpenAI API key set as an environment variable:

```bash
export OPENAI_API_KEY=your_api_key
```

To use the Google search engine, set up a Google Custom Search JSON API by visiting [Google Developers](https://developers.google.com/custom-search/v1/overview). Set the API key as an environment variable:

```bash
export GOOGLE_CUSTOM_API_KEY=your_api_key
```

## Running the script
Go to the verifact directory, then, run the script using the following command:
```bash
python subprocess_verify.py -i the_input_file_path -s the_search_engine
```
Valid search engines are "DuckDuckGo" and "Google". DuckDuckGo is used as the default search engine if -s the_search_engine is not specified.

To see an example of the script in action, run:
```bash
python subprocess_verify.py -i fact.json
```
In the verifact directory.