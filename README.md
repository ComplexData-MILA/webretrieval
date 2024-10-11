# Web Retrieval Agents for Evidence-Based Misinformation Detection

This repository contains the Python script for a two-agent search system designed to detect misinformation based on evidence. The approach leverages web retrieval agents to verify facts against trusted sources. For an in-depth explanation of the methodology and system architecture, please refer to our paper: [Web Retrieval Agents for Evidence-Based Misinformation Detection](https://arxiv.org/abs/2409.00009).

## Prerequisites
This project takes a JSON file as input and verifies all facts in parallel using a search engine and the ChatGPT API. Refer to the fact.json file in the verifact directory for the format of the JSON file.

Before running the script, ensure that all necessary Python packages are installed. You can install these packages using pip:

```bash
pip install -r requirements.txt
```
Then, run the script using the following command:
```bash
python subprocess_verify.py
```

