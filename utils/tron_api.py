import requests
import base58
from tronapi import Tron
tron = Tron().address


class TronAPI:

    def __init__(self,base_url=None,private_key=None,owner_address=None,contract_address=None):
        self.base_url = base_url
        self.visible = None
        self.tx_id = None
        self.raw_data = None
        self.raw_data_hex = None
        self.signature = None
        self.private_key = private_key
        self.owner_address = owner_address
        self.contract_address = contract_address


    def transfer(self,address,amount):
        url = f"{self.base_url}/wallet/triggersmartcontract"

        amount = '0'*(64- len(hex(amount)[2:])) + hex(amount)[2:]

        address = self.to_hex(address)
        address = '0'*(64- len(address[2:])) + address[2:]

        parameter = address + amount
        payload = {
            "owner_address": self.owner_address,
            "contract_address": self.contract_address,
            "function_selector": "transfer(address,uint256)",
            "call_value": 0,
            "fee_limit": "100000000",
            "visible": True,
            "parameter": parameter
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        response = response.json()

        self.visible = response['transaction']['visible']
        self.tx_id = response['transaction']['txID']
        self.raw_data = response['transaction']['raw_data']
        self.raw_data_hex = response['transaction']['raw_data_hex']

        self._sign_transaction()
        return self._broadcast_transaction()

    def _sign_transaction(self):
        url = f"{self.base_url}/wallet/gettransactionsign"

        payload = {
            "transaction": {
                "raw_data": str(self.raw_data),
                "raw_data_hex": self.raw_data_hex,
                "visible": True,
                "txID": self.tx_id
            },
            "privateKey": self.private_key
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        response = response.json()

        self.visible = response['visible']
        self.signature = response['signature']
        self.tx_id = response['signature']
        self.raw_data = response['raw_data']
        self.raw_data_hex = response['raw_data_hex']

    def _broadcast_transaction(self):
        url = f"{self.base_url}/wallet/broadcasttransaction"

        payload = {
            "raw_data": str(self.raw_data),
            "raw_data_hex": self.raw_data_hex,
            "signature": self.signature,
            "txID": self.tx_id,
            "visible": self.visible
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        return response.json()

    def to_hex(self,address):
        return tron.to_hex(address).lower()
        
    def to_base58(self,address):
        return tron.from_hex(address).decode("utf-8") 

    def get_transaction_history(self,address,only_confirmed=True,only_to=True,min_timestamp=0):
        url = f'{self.base_url}/v1/accounts/{address}/transactions/trc20'
        params = {
            'only_confirmed' : only_confirmed,
            'only_to' : only_to,
            'limit': 200,
            'min_timestamp': min_timestamp
        }
        response = requests.get(url,params=params)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return False
