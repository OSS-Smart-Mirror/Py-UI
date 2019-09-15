from __future__ import print_function
import time
import intrinio_sdk
from intrinio_sdk.rest import ApiException

def get_stonks():
    intrinio_sdk.ApiClient().configuration.api_key['api_key'] = 'API-KEY'
    security_api = intrinio_sdk.SecurityApi()
    identifiers = ['AAPL', 'MSFT', 'GS', 'NKE']
    price_list = list()
    try:
        for identifier in identifiers:
            api_response = security_api.get_security_realtime_price(identifier)
            price_list.append((identifier, api_response.ask_price))
    except ApiException as e:
        print("Exception when calling SecurityApi->get_security_realtime_price: %s\r\n" % e)
    finally:
        return price_list

if __name__ == "__main__":
    print(get_stonks())
