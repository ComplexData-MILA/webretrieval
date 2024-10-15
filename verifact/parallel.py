"""
Standalone script demonstrating the logic behind
https://arxiv.org/abs/2409.00009 with DuckDuckGo search.
"""
import time
from dotenv import load_dotenv
load_dotenv()
import search_engine
import re
from typing import Any, Optional, NamedTuple
import os
import json
import openai
import pandas as pd
from duckduckgo_search import DDGS
import sys


MAX_NUM_TURNS: int = 10
MAIN_AGENT_MODEL_NAME: str = sys.argv[3] #this file should only be call from subprocess_verify, hence guarantee this argument exist.
MAX_SEARCH_RESULTS: int = 10


def _query_initial(statement):

    initial_query = f"""\
    You have access to a search engine tool. To invoke search, \
    begin your query with the phrase "SEARCH: ". You may invoke the search \
    tool as many times as needed. 

    Your task is to analyze the factuality of the given statement.

    Statement: {statement}

    After providing all your analysis steps, summarize your analysis \
    and state "True statement; Factuality: 1" if you think the statement \
    is factual, or "False statement; Factuality: 0" otherwise.
    """

    context: Any = [{"role": "user", "content": initial_query}]

    return context

def search(query: str, engine) -> str:
    """
    Invoke web search.

    Params:
        query: str

    Returns:
        Summarized response to search query.
    """
    res = ""
    if engine == "DuckDuckGo":
        results = DDGS().text(query, max_results=MAX_SEARCH_RESULTS * 2)
        results = [r for r in results if "politifact.com" not in r.get("href")][:MAX_SEARCH_RESULTS]
        for doc in results:
            res += f"Title: {doc['title']} Content: {doc['body'][:1600]}\n"

    elif engine == "Google":
        results = search_engine.google_search(query, MAX_SEARCH_RESULTS * 2)
        results = [r for r in results if "politifact.com" not in r.get("link")][:MAX_SEARCH_RESULTS]
        for doc in results:
            res += f"Title: {doc['title']} Content: {doc['snippet'][:1600]}\n"
    response = openai.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"Please summarize the searched information for the query. Summarize your findings, taking into account the diversity and accuracy of the search results. Ensure your analysis is thorough and well-organized.\nQuery: {query}\nSearch results: {res}",
        }], 
        model=MAIN_AGENT_MODEL_NAME
    ).choices[0].message.content
    return response


class _KeywordExtractionOutput(NamedTuple):
    """Represent the part up to the matched string, and the match itself."""

    content_up_to_match: str
    matched_content: str


def _extract_search_query_or_none(
    assistant_response: str,
) -> Optional[_KeywordExtractionOutput]:
    """
    Try to extract "SEARCH: query\\n" request from the main agent response.

    Discards anything after the "query" part.

    Returns:
        _KeywordExtractionOutput if matched.
        None otherwise.
    """
    match = re.search(r"(.*?SEARCH:\s+)(.+?)(\s*$)", assistant_response, re.DOTALL | re.MULTILINE)
    if match is None:
        return None
    return _KeywordExtractionOutput(
        content_up_to_match=match.group(1) + match.group(2),
        matched_content=match.group(2),
    )


def _extract_prediction_or_none(assistant_response: str) -> Optional[str]:
    """
    Try to extract "Factuality: 1" (or 0, or 0.5) from main agent response.

    Response:
        Prediction value (as a string) if matched.
        None otherwise.
    """

    match = re.search(r"Factuality:\s(\d+\.?\d?)", assistant_response)
    if match is None:
        return None

    return match.group(1)

def process_statement(statement, engine, output):
    context = _query_initial(statement)
    for turns in range(MAX_NUM_TURNS):
        response = openai.chat.completions.create(
            messages=context, model=MAIN_AGENT_MODEL_NAME
        )
        main_agent_message = response.choices[0].message.content
        assert main_agent_message is not None, (
            "Invalid Main Agent API response:",
            response,
        )

        # If search is requested in a message, truncate that message
        # up to the search request. (Discard anything after the query.)
        search_request_match = _extract_search_query_or_none(main_agent_message)
        if search_request_match is not None:
            search_response = search(search_request_match.matched_content,engine)
            context += [
                {"role": "assistant", "content": search_request_match.content_up_to_match},
                {"role": "user", "content": f"Search result: {search_response}"},
            ]
            continue
        else:
            context += [{"role": "assistant", "content": main_agent_message}]

        prediction_match = _extract_prediction_or_none(main_agent_message)
        if prediction_match is not None:
            output_data = {
                "statement": statement,
                "engine_used": engine,
                "interaction": turns,
                "prediction": prediction_match
            }

            if not os.path.isfile(output_file):
                with open(output_file, 'w') as file:
                    json.dump([output_data], file, indent=4)
            else:
                with open(output_file, 'r+') as file:
                    data = json.load(file)
                    data.append(output_data)
                    file.seek(0)
                    json.dump(data, file, indent=4)
            break


if __name__ == "__main__":
    if len(sys.argv) > 4:
        statement_arg = sys.argv[1] #the statement
        engine = sys.argv[2] #the engine
        output_file = sys.argv[4] #the output file_path
        process_statement(statement_arg, engine,output_file)
    else:
        print("statement and engine type should be provided")