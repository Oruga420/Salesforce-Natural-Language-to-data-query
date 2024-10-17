import os
import json
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def send_openai_request(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content

def interpret_query(user_query: str) -> dict:
    prompt = f"""Interpret this Salesforce query: '{user_query}'.
    Identify the Salesforce object and relevant fields.
    Return a JSON object with 'object' and 'fields' keys.
    Example: {{"object": "Account", "fields": ["Name", "Industry"]}}"""
    
    response = send_openai_request(prompt)
    return json.loads(response)

def generate_soql(interpreted_query: dict) -> str:
    object_name = interpreted_query['object']
    fields = ', '.join(interpreted_query['fields'])
    prompt = f"""Generate a SOQL query to retrieve {fields} from {object_name}.
    Return only the SOQL query string.
    Example: "SELECT Name, Industry FROM Account LIMIT 10" """
    
    response = send_openai_request(prompt)
    return json.loads(response)["query"]

def format_response(soql_result: dict) -> str:
    prompt = f"""Format the following Salesforce query result for a user-friendly response:
    {json.dumps(soql_result)}
    Provide a concise summary of the data retrieved.
    """
    
    response = send_openai_request(prompt)
    return json.loads(response)["summary"]
