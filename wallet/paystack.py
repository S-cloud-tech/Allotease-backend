from django.conf import settings
import requests
import json


class Paystack:
    PAYSTACK_TEST_SECRET_KEY = settings.PAYSTACK_TEST_SECRET_KEY
    base_url = "https://api.paystack.co"


    headers = {
            "Authorization": f"Bearer {PAYSTACK_TEST_SECRET_KEY}",
            "Content-Type": "application/json",
        }
    def create_customer(self,email,first_name,last_name,phone):
        path = "/customer"
        url = self.base_url + path
        data1={
            "email": f"{email}",
            "first_name": f"{first_name}",
            "last_name": f"{last_name}",
            "phone": phone,
        }
        data2 = json.dumps(data1 , indent=4)
        response = requests.post(url=url , headers=self.headers , data=data2)
        print(response)
        print(response.json())
        if response.status_code == 200:
            response_data = response.json()
            data =response_data['data']
            status = response_data['status']
            return status,data
        else:
            return False,"failed"

    def validate_bvn(self,account_number,bank_code):
        print(bank_code)
        print(account_number)
        path = f"/bank/resolve?account_number={account_number}&bank_code={bank_code}"
        url = self.base_url + path
        
        response = requests.get(url=url , headers=self.headers )
        response_data = response.json()
        if response.status_code == 200:
            data =response_data['data']
            status = response_data['status']        
        else:
            data =response_data['message']
            status = response_data['status']
        return status,data

    def validate_customer(self,account_number,customer_code,bvn,bank_code,fname,lname,country):
        path = f"/customer/{customer_code}/identification"
        url = self.base_url + path
        data1={
            "country": f"{country}",
            "type": f"bank_account",
            "account_number": f"{account_number}",
            "bvn": f"{bvn}",
            "bank_code": f"{bank_code}",
            "first_name": f"{fname}",
            "last_name": f"{lname}"
        }
        data2 = json.dumps(data1 , indent=4)
        response = requests.post(url=url , headers=self.headers , data=data2)
        if response.status_code == 202:
            response_data = response.json()
            data =response_data['message']
            status = response_data['status']
            return status,data
        else:
            return False,"failed"

    def create_virtual_account(self,customer):
        # print(customer)
        path = "/dedicated_account"
        url = self.base_url + path
        data1={
            "customer":f"{customer}",
            "preferred_bank":"wema-bank"
        }
        data2 = json.dumps(data1 , indent=4)
        response = requests.post(url=url , headers=self.headers , data=data2)
        # print(response.json())
        if response.status_code == 200:
            response_data = response.json()
            data =response_data['data']
            status = response_data['status']
            print(response_data)
            return status,data
        else:
            return False,"failed"

    def verify_account(self,account_number,bank_code):
        path = f"/bank/resolve?account_number={account_number}&bank_code={bank_code}"
        url = self.base_url + path
        response = requests.get(url=url , headers=self.headers)
        if response.status_code == 200:
            response_data = response.json()
            data =response_data['data']
            status = response_data['status']
            return status,data
        else:
            return False,"failed"

    def create_recipient(self,name,account_number,bank_code,currency):
        path = "/transferrecipient"
        url = self.base_url + path
        data1={
            "type": "nuban",
            "name": f"{name}",
            "account_number": f"{account_number}",
            "bank_code": f"{bank_code}",
            "currency": f"{currency}"
        }
        data2 = json.dumps(data1 , indent=4)
        response = requests.post(url=url , headers=self.headers , data=data2)
        if response.status_code == 200:
            response_data = response.json()
            data =response_data['data']
            status = response_data['status']
            return status,data
        else:
            return False,"failed"
    
    def transfer(self,recipient,amount,currency,reason):
        path = "/transfer"
        url = self.base_url + path
        data1={
            "source": "balance", 
            "reason": f"{reason}", 
            "amount": amount, 
            "recipient": f"{recipient}",
            "currency": f"{currency}",
        }
        data2 = json.dumps(data1 , indent=4)
        response = requests.post(url=url , headers=self.headers , data=data2)
        if response.status_code == 200:
            response_data = response.json()
            data =response_data['data']
            status = response_data['status']
            return status,data
        else:
            return False,"failed"

    def bulk_transfer(self,transfers):
        path = "/transfer/bulk"
        url = self.base_url + path
        data1={
            "currency": "NGN",
            "source": "balance",
            "transfers": transfers,
        }
        data2 = json.dumps(data1 , indent=4)
        response = requests.post(url=url , headers=self.headers , data=data2)
        if response.status_code == 200:
            response_data = response.json()
            data =response_data['data']
            status = response_data['status']
            return status,data
        else:
            return False,"failed"