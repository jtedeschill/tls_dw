from tasks import hubspot_tasks
from hubspot import HubSpot
import os
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


hubspot_token = os.getenv("HUBSPOT_TOKEN")
client = HubSpot(access_token=hubspot_token)

endpoints = {
    "companies": client.crm.companies,
    "contacts": client.crm.contacts,
    "deals": client.crm.deals,
}
def get_endpoint(endpoint, properties, after=None):
    logging.debug(f"Getting data from {endpoint}")

    api_response = endpoint.basic_api.get_page(limit=100, properties=properties, after=after, archived=False)
    for item in api_response.results:
        yield item.properties

    if api_response.paging and api_response.paging.next:
        after = api_response.paging.next.after
        yield from get_endpoint(endpoint, properties, after)



for table, endpoint in endpoints.items():
    properties = hubspot_tasks[table]["properties"]
    logging.debug(f"Getting data from {table}")
    
    data = pd.DataFrame.from_records(list( get_endpoint(endpoint, properties)))
    print(data)