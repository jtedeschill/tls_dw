import requests
from dotenv import load_dotenv
import os
import logging
from urllib.parse import urlparse
import pandas as pd
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



class BullhornClient:
    """Bullhorn API client for authenticating and making requests to the Bullhorn API.

    Attributes:
        username (str): The username for authentication.
        password (str): The password for authentication.
        client_id (str): The client ID for authentication.
        client_secret (str): The client secret for authentication.
        token (str): The access token obtained after authentication.
        refresh_token (str): The refresh token obtained after authentication.
    """

    def __init__(self, username, password, client_id, client_secret):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.refresh_token = None
        self.rest_token = None
        self.rest_url = None

        logging.debug('Initialized BullhornClient')

    def _parse_auth_code(self, response):
        location = response.headers['Location']
        parsed_url = urlparse(location)
        query = parsed_url.query
        query_params = dict(qc.split('=') for qc in query.split('&'))
        logging.debug(f'Parsed auth code: {query_params["code"]}')
        self.client_id = query_params['client_id']
        return query_params['code']
    

    def _get_auth_code(self, username, password, client_id):
        url = 'https://auth-west.bullhornstaffing.com/oauth/authorize'
        params = {
            'client_id': client_id,
            'response_type': 'code',
            'username': username,
            'password': password,
            'action': 'Login'
        }
        response = requests.get(url, params=params, allow_redirects=False)
        
        if response.status_code == 302:
            # parse the location header to get the auth code
            return self._parse_auth_code(response)
        else:
            return response
    
    def _get_token(self, auth_code):
        url = 'https://auth-west.bullhornstaffing.com/oauth/token'

        full_url = f'{url}?grant_type=authorization_code&code={auth_code}&client_id={self.client_id}&client_secret={self.client_secret}'
        logging.debug(f'Making post request to {full_url}')
        response = requests.post(full_url)

        
        json_data = response.json()
        if 'access_token' in json_data:
                self.token = json_data['access_token']
                self.refresh_token = json_data['refresh_token']
                return response
        else:
            print(response.json())
            raise Exception('Failed to get token')

    def authenticate(self):
        auth_code = self._get_auth_code(self.username, self.password, self.client_id)
        self._get_token(auth_code)
        logging.debug('Authenticated successfully')
        self._login_rest_api()
        
    def get_refresh_token(self):
        url = f"https://auth-west.bullhornstaffing.com/oauth/token?grant_type=refresh_token&refresh_token={self.refresh_token}&client_id={self.client_id}&client_secret={self.client_secret}"
        response = requests.post(url)
        if response.headers.get('Content-Type').startswith('application/json'):
            jsonData = response.json()
            if 'access_token' in jsonData and 'refresh_token' in jsonData:
                self.token = jsonData['access_token']
                self.refresh_token = jsonData['refresh_token']
                return self.token
        return None
    
    # Step 5: Log into the Rest API
    def _login_rest_api(self):
        url = f"https://rest-west.bullhornstaffing.com/rest-services/login?version=*&access_token={self.token}"
        response = requests.get(url)
        if response.headers.get('Content-Type').startswith('application/json'):
            jsonData = response.json()

            if 'BhRestToken' in jsonData and 'restUrl' in jsonData:
                self.rest_token = jsonData['BhRestToken']
                self.rest_url = jsonData['restUrl']
                return self.rest_token
        return None
        
    def make_request(self, endpoint, fields, query, count, start):
        """Make a request to the Bullhorn API.

        Args:
            endpoint (str): The endpoint to make the request to.
            fields (str): The fields to retrieve.
            query (str): The query to filter the data.
            count (int): The number of records to retrieve.
            start (int): The starting index to retrieve the data.

        Returns:

        """       
        if count < 1:
            return  # Base case: if count is less than 1, stop the recursion

        restUrl = self.rest_url
        BhRestToken = self.rest_token
        params = {
            'fields': fields,
            'where': query,
            'count': count,
            'start': start,
            'BhRestToken': BhRestToken
        }

        response = requests.get(f'{restUrl}/query/{endpoint}', params=params)

        data = response.json()

        if len(data.get('data', [])) < count:
            # If the data length is less than count, retry with a smaller count
            logging.debug(f'Retrying with count {count//2}')
            yield from self.make_request(endpoint, fields, query, count//2, start)
        else:
            logging.debug(f'Start: {start}, Count: {count}')
            start += count
            for item in data['data']:
                yield item
            # Recursively call the function to continue fetching data
            yield from self.make_request(endpoint, fields, query, count, start)

            
    


if __name__ == '__main__':
    load_dotenv()
    BH = BullhornClient(os.getenv('BH_USERNAME'), os.getenv('BH_PASSWORD'), os.getenv('BH_CLIENT_ID'), os.getenv('BH_CLIENT_SECRET'))
    BH.authenticate()

    df = pd.DataFrame.from_records(BH.make_request('ClientContact', 'id,name,email', 'dateAdded>1000000000000', 500, 69000))
    print(df)




