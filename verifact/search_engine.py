import re
import requests
import json
from pprint import pprint
import requests
import os
#this file contain a list of websearch api key I implement for test

def google_search(query, result_total=10):
    """
    Conducts a Google search using the provided query and retrieves a specified number of results.
    
    :param query: The search query string.
    :param result_total: Total number of results desired.
    """
    def build_payload(query, start=1, num=10, **params):
        """
        Builds the payload for the Google Search API request.

        :param query: Search term.
        :param start: The index of the first result to return.
        :param num: Number of search results per request.
        :param params: Additional parameters for the API request.
        :return: Dictionary containing the API request parameters.
        """
        api_key = os.getenv("GOOGLE_CUSTOM_API_KEY")
        payload = {
            'key':api_key,
            'q': query,
            'cx': '43df6c4509ec4403a',
            'start': start,
            'num': num,
        }
        payload.update(params)
        return payload

    def make_request(payload):
        """
        Sends a GET request to the Google Search API and handles potential errors.

        :param payload: Dictionary containing the API request parameters.
        :return: JSON response from the API.
        """
        response = requests.get('https://www.googleapis.com/customsearch/v1', params=payload)
        if response.status_code != 200:
            raise Exception('Request failed with status code {}'.format(response.status_code))
        return response.json()

    items = []
    pages = (result_total + 9) // 10  # Ensuring we account for all pages including the last one which might be partial
    for i in range(pages):
        start_index = i * 10 + 1
        num_results = 10 if i < pages - 1 else result_total - (i * 10)
        payload = build_payload(query, start=start_index, num=num_results)
        response = make_request(payload)
        items.extend(response.get('items', []))

    return items


def brave_search(query, result_total = 10):
    
    def extract_web_search_data(response):
        response_data = json.loads(response.text)
        web_search_results = response_data['web'].get('results', [])
        for result in web_search_results:
            title = result.get('title', 'no title')  
            snippet = result.get('description', 'no description')  
            url = result.get('url', 'no link') 
            print(f"title: {title}")
            print(f"snippet: {snippet}")
            print(f"link: {url}")
            print("-" * 30)  
            
    response = requests.get(
        url="https://api.search.brave.com/res/v1/web/search",
        headers={
            'Accept': 'application/json',
            'X-Subscription-Token': 'key here'
        },
        params={
            'q': query,
            'count': result_total
        }
    )
    if response.status_code == 200:
        extract_web_search_data(response)
    else:
        print(f"wrong response: code {response.status_code}")
        print(response.text) 
    

def bing_search(query,count):
    '''
    This sample makes a call to the Bing Web Search API with a query and returns relevant web search.
    Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
    '''

    # Add your Bing Search V7 subscription key and endpoint to your environment variables.
    #subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
    endpoint = "https://api.bing.microsoft.com/v7.0/search"

    # Query term(s) to search for. 

    # Construct a request
    mkt = 'en-US'
    params = { 'q': query, 'mkt': mkt, "count":count }
    headers = { 'Ocp-Apim-Subscription-Key': "key here" }

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()

        print("Headers: ")
        print(response.headers)

        print("JSON Response:  ")
        pprint(response.json())
    
    except Exception as ex:
        raise ex
        

# Example usage:
if __name__ == "__main__":
    google_search("donald trump date of birth",10)

