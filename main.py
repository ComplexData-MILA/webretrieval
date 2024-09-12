"""
Standalone script demonstrating the logic behind
https://arxiv.org/abs/2409.00009
"""

import re
from typing import Any, Optional, NamedTuple

import openai

MAX_NUM_TURNS: int = 10
MAIN_AGENT_MODEL_NAME: str = "gpt-4o-mini"

statement = input("Enter statement to verify and press ENTER: ")

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


def search(query: str) -> str:
    """
    Invoke web search.

    Params:
        query: str
        (please feel free to add other parameters as needed.)

    Returns:
        Summarized response to search query.
    """
    return "TODO: Search and Summarize"


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

    match = re.match(r"(.*SEARCH:\s+)(.+)([\n]+.+)", assistant_response)
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

    match = re.search(r"Factuality:\s(\d+\.?\d+)", assistant_response)
    if match is None:
        return None

    return match.group(1)


for _ in range(MAX_NUM_TURNS):
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
        search_response = search(search_request_match.matched_content)
        context += [
            {"role": "assistant", "content": search_request_match.content_up_to_match},
            {"role": "user", "content": f"Search result: {search_response}"},
        ]
        continue
    else:
        context += [{"role": "assistant", "content": main_agent_message}]

    prediction_match = _extract_prediction_or_none(main_agent_message)
    if prediction_match is not None:
        print(f"Prediction: {prediction_match}")
        break
