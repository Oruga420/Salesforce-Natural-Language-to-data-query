from simple_salesforce import Salesforce

def authenticate_salesforce(access_token: str, instance_url: str) -> Salesforce:
    return Salesforce(instance_url=instance_url, session_id=access_token)

def execute_soql_query(sf: Salesforce, query: str) -> dict:
    try:
        result = sf.query(query)
        return result
    except Exception as e:
        raise Exception(f"Error executing SOQL query: {str(e)}")
