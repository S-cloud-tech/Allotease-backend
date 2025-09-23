from django.conf import settings
import requests
import secrets
import json

class Kuda_model:
    if settings.KUDA_TEST == "True":
        KUDA_SECRET_KEY = settings.KUDA_KEY
        KUDA_EMAIL = settings.KUDA_EMAIL
        base_url = settings.KUDA_BASE_URL
    else:
        KUDA_SECRET_KEY = settings.KUDA_KEY
        KUDA_EMAIL = settings.KUDA_EMAIL
        base_url = settings.KUDA_BASE_URL

    def get_request_ref():
        s = secrets.SystemRandom()
        ref = s.randint(10000000, 99999999)
        return ref

    def format_amount(amount):
        return int(amount*100)

    def truncate_string(s):
        new = s
        if len(s) > 30:
            new = s[:30]
        return new

    def get_credentials(self) : 
        
        url = self.base_url + "/Account/GetToken"
        
        payload = json.dumps({
            "email": self.KUDA_EMAIL,
            "apiKey": self.KUDA_SECRET_KEY
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        return response.text

    def execute_kuda_call(self,endpoint = '', payload= {}) : 
 
        token = self.get_credentials()
        if not token : 
            return False

        url = self.base_url + endpoint
        
        payload = json.dumps(payload)
        
        headers = {
            'Authorization': f'bearer {token}',
            'Content-Type': 'application/json'
            }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        try : 
            return response
        except : 
            return False

    def create_virtual_account(self,tracking_ref,email,phone,business_name,lastname,firstname):
        ref = self.get_request_ref()
        data1={
            "data":"{\"servicetype\":\"ADMIN_CREATE_VIRTUAL_ACCOUNT\",\"requestref\":\""+str(ref)+"\",\"data\":{\"email\":\""+str(email)+"\",\"phoneNumber\":\""+str(phone)+"\",\"lastName\":\""+str(lastname)+"\",\"firstName\":\""+str(firstname)+"\",\"businessName\":\""+str(business_name)+"\",\"trackingReference\":\""+str(tracking_ref)+"\"}}"
        }

        data2={
            "data":"{\"servicetype\": \"ADMIN_RETRIEVE_SINGLE_VIRTUAL_ACCOUNT\",\"requestref\": \""+str(ref)+"\",\"data\" : {\"trackingReference\" : \""+str(tracking_ref)+"\"}}"
        }

        response = self.execute_kuda_call('',data1)

        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            if status == True:
                response1 = self.execute_kuda_call('',data2)
                if response1.status_code == 200:
                    data1 =json.loads(json.loads(response1.text)['data'])
                    status1 = data1['Status']
                    return status1,data1
                else:
                    return False,"Account created but Something went wrong"
            else:
                return False,data['Message']
        else:
            return False,"Somthing went wrong."

    def get_virtual_account(self,tracking_ref):
        ref = self.get_request_ref()
        data1={
            "data":"{\"servicetype\": \"ADMIN_RETRIEVE_SINGLE_VIRTUAL_ACCOUNT\",\"requestref\": \"GVA"+str(ref)+"\",\"Data\" : {\"trackingReference\" : \""+str(tracking_ref)+"\"}}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"
    
    def disable_virtual_account(self,tracking_ref):
        ref = self.get_request_ref()
        data1={
            "data":"{\"serviceType\":\"ADMIN_DISABLE_VIRTUAL_ACCOUNT\",\"requestRef\":\"DVA"+str(ref)+"\",\"data\": {\"trackingReference\":\""+str(tracking_ref)+"\"}}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"

    def enable_virtual_account(self,tracking_ref):
        ref = self.get_request_ref()
        data1={
            "data":"{\"serviceType\":\"ADMIN_ENABLE_VIRTUAL_ACCOUNT\",\"requestRef\":\"EVA"+str(ref)+"\",\"data\": {\"trackingReference\":\""+str(tracking_ref)+"\",}}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"

    def update_virtual_account(self,tracking_ref,user,first,last):
        ref = self.get_request_ref()

        data1={
           "data": "{\"serviceType\":\"ADMIN_UPDATE_VIRTUAL_ACCOUNT\",\"requestRef\":\"UVA"+str(ref)+"\",\"data\": {\"trackingReference\": \""+str(tracking_ref)+"\",\"FirstName\":\""+str(first)+"\",\"LastName\":\""+str(last)+"\", \"Email\":\""+str(user.email)+"\",}}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"

    def verify_account(self,tracking_ref,bank_code,account_number):
        ref = self.get_request_ref()

        data1={
            "data":"{\"serviceType\": \"NAME_ENQUIRY\",\"requestRef\": \"VA"+str(ref)+"\",\"data\": {\"beneficiaryAccountNumber\": \""+str(account_number)+"\",\"beneficiaryBankCode\": \""+str(bank_code)+"\",\"SenderTrackingReference\": \""+str(tracking_ref)+"\",\"isRequestFromVirtualAccount\":\"true\"},}"
        }#True or False value. If the intended transfer is to be made by the virtual account
        #Tracking reference of the virtual account trying to do the actual transfer. Leave it empty if the intended transfer is going to be from the main account

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            print(data)
            return status,data
        else:
            return False,"Something went wrong"

    def get_account_name1(self,bank_code,account_number):
        ref = self.get_request_ref()

        data1={
            "data":"{\"serviceType\": \"NAME_ENQUIRY\",\"requestRef\": \"VA"+str(ref)+"\",\"data\": {\"beneficiaryAccountNumber\": \""+str(account_number)+"\",\"beneficiaryBankCode\": \""+str(bank_code)+"\",\"SenderTrackingReference\": \"\",\"isRequestFromVirtualAccount\":\"false\"},}"
        }#True or False value. If the intended transfer is to be made by the virtual account
        #Tracking reference of the virtual account trying to do the actual transfer. Leave it empty if the intended transfer is going to be from the main account

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            print(data)
            return status,data
        else:
            return False,"Something went wrong"

    def tranfer(self,tracking_ref,account_number,amount,narration,bank_code,name,business_name,session_id):
        amount = self.format_amount(amount)
        ref = self.get_request_ref()

        data1={
            "data":"{\"serviceType\": \"VIRTUAL_ACCOUNT_FUND_TRANSFER\",\"requestRef\": \""+str(ref)+"\",\"data\": {\"trackingReference\": \""+str(tracking_ref)+"\",\"beneficiaryAccount\": \""+str(account_number)+"\",\"amount\": \""+str(amount)+"\",\"narration\": \""+str(narration)+"\",\"beneficiaryBankCode\": \""+str(bank_code)+"\",\"beneficiaryName\": \""+str(name)+"\",\"senderName\": \""+str(business_name)+"\",\"nameEnquiryId\": \""+str(session_id)+"\",},}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            ref = data['TransactionReference']
            return status,ref
        else:
            return False,"Something went wrong"

    def withdraw(self,tracking_ref,amount,narration):
        ref = self.get_request_ref()
        amount = int(amount - 20)
        if int(amount) >= 10000:
            amount = amount - int(50)
        amount = self.format_amount(amount)
        data1={
            "data":"{\"serviceType\": \"WITHDRAW_VIRTUAL_ACCOUNT\",\"requestRef\": \""+str(ref)+"\",\"data\": {\"trackingReference\": \""+str(tracking_ref)+"\",\"amount\": \""+str(amount)+"\",\"narration\": \""+str(narration)+"\"}}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            print(data)
            ref = data['TransactionReference']
            return status,ref
        else:
            return False,"Something went wrong"

    def get_virtual_account_balance(self,tracking_ref):
        ref = self.get_request_ref()
        data1={
            "data":"{\"serviceType\": \"RETRIEVE_VIRTUAL_ACCOUNT_BALANCE\",\"requestRef\": \"GVAB"+str(ref)+"\",\"data\": { \"trackingReference\": \""+str(tracking_ref)+"\"}}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"

    def get_account_name(self,tracking_ref,bank_code,account_number):
        ref = self.get_request_ref()
        data1={
            "data":"{\"serviceType\": \"NAME_ENQUIRY\",\"requestRef\": \"VA"+str(ref)+"\",\"data\": {\"beneficiaryAccountNumber\": \""+str(account_number)+"\",\"beneficiaryBankCode\": \""+str(bank_code)+"\",\"SenderTrackingReference\": \" \",\"isRequestFromVirtualAccount\":\" \"},}"
        }
        
        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            if status == True:
                return status,data['Data']['BeneficiaryName']
            return False,"Something went wrong"
        else:
            return False,"Something went wrong"
            
    def get_transactions_history(self,tracking_ref,startDate,endDate):
        ref = self.get_request_ref()

        data1={
            "data":"{\"serviceType\": \"ADMIN_VIRTUAL_ACCOUNT_FILTERED_TRANSACTIONS\",\"requestRef\": \""+str(ref)+"\",\"data\": {\"trackingReference\": \""+str(tracking_ref)+"\",\"pageSize\":\" 1\",\"startDate\": \""+str(startDate)+"\",\"endDate\": \" "+str(endDate)+"\"},}"
        }

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"

    def get_bank_list(self):
        ref = self.get_request_ref()
        data1={"data":"{\"serviceType\": \"BANK_LIST\",\"requestRef\": \"BL"+str(ref)+"\",}"}

        response = self.execute_kuda_call('',data1)
        if response.status_code == 200:
            data =json.loads(json.loads(response.text)['data'])
            status = data['Status']
            return status,data
        else:
            return False,"Something went wrong"
