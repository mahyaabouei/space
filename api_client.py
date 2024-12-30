from pymongo import MongoClient
import requests
import json
import pandas as pd
from datetime import datetime
class Tle :
    def __init__(self ):
        self.host = '192.168.11.13'
        self.port = 27017
        connection_string = f"mongodb://{self.host}:{self.port}/"
        
        self.API_URL = "http://127.0.0.1:8000/"
        self.client = MongoClient(connection_string)
        self.database = self.client['farasahm2']
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NDc3NzQ2LCJpYXQiOjE3MzU0NjMzNDYsImp0aSI6IjJmNTVjODY0OTUzOTRiNGU5Zjc0MDE4NWU5YTU0NjEzIiwidXNlcl9pZCI6M30.LBgv2rsgf8V8DASaLlbkLBZdJQBMmrtvlGCeS5avXr8"
        }

    
    def tle_sejam(self):
        collection = self.database['sejam']
        for item in collection.find():
            del item['_id']
            response = requests.post(self.API_URL + 'sejam-data-receiver/', json=item)
            print(response.json())


    def tle_shareholders(self):
            collection = self.database['registerNoBours'].find({"symbol":"fevisa","date":14030908})
            users = requests.get(self.API_URL + 'users/', headers=self.headers)
            users = pd.DataFrame(users.json())
            print(users)
            for item in collection:
                avaliable_user = item['کد ملی'] in users['username'].values
                if not avaliable_user:
                    dict = {
                        "uniqueIdentifier":item['کد ملی'],
                        "email": item['کد ملی']+"@gmail.com",
                        "mobile":'00000000000',
                        "status":True,
                        "is_sejam_registered":False,
                        "privatePerson":{
                            "gender":"Male",
                            "first_name": 'نامشخص',
                            "last_name": 'نامشخص',
                        }
                    }

                    response = requests.post(self.API_URL + 'sejam-data-receiver/', json=dict)
                    if response.status_code >= 300:
                        print(response.json())
                        break

                users = requests.get(self.API_URL + 'users/', headers=self.headers)
                users = pd.DataFrame(users.json())
                
                company = requests.get(f"{self.API_URL}companies/", headers=self.headers)
                company = pd.DataFrame(company.json())
                company_id = company.id.values[0]  
                print(company_id)
                number_of_shares = int(item['تعداد سهام'])
                sharehilder_detail = {
                    "user": int(users[users['uniqueIdentifier'] == item['کد ملی']].id.values[0]),
                    "company": int(company_id),
                    "number_of_shares": number_of_shares,
                }
                shareholder = requests.post(self.API_URL + 'stock_affairs/shareholders/', headers=self.headers, json=sharehilder_detail)
                
                if shareholder.status_code < 300:
                    continue
                print(f"Response: {shareholder.json()}")
                if shareholder.json()['error'] ==  'این کاربر قبلاً در این شرکت به عنوان سهامدار ثبت شده است':
                    continue
                break
    

    def tle_precedence(self) :
        collection = self.database['Priority'].find({"symbol":"fevisa","dateInt":14030728})
        users = requests.get(self.API_URL + 'users/', headers=self.headers)
        users = pd.DataFrame(users.json())
        print(users)
        for item in collection:
            avaliable_user = item['کد ملی'] in users['username'].values
            if not avaliable_user:
                dict = {
                    "uniqueIdentifier":item['کد ملی'],
                    "email": item['کد ملی']+"@gmail.com",
                    "mobile":'00000000000',
                    "status":True,
                    "is_sejam_registered":False,
                    "privatePerson":{
                        "gender":"Male",
                        "first_name": 'نامشخص',
                        "last_name": 'نامشخص',
                    }
                }

                response = requests.post(self.API_URL + 'sejam-data-receiver/', json=dict)
                if response.status_code >= 300:
                    print(response.json())
                    break

            users = requests.get(self.API_URL + 'users/', headers=self.headers)
            users = pd.DataFrame(users.json())
            
            company = requests.get(f"{self.API_URL}companies/", headers=self.headers)
            company = pd.DataFrame(company.json())
            company_id = company.id.values[0]  
            print(company_id)
            precedence = int(item['حق تقدم'])
            precedence_detail = {
                "user": int(users[users['uniqueIdentifier'] == item['کد ملی']].id.values[0]),
                "company": int(company_id),
                "precedence": precedence,
            }
            precedence = requests.post(self.API_URL + 'stock_affairs/precedence/', headers=self.headers, json=precedence_detail)
            
            if precedence.status_code < 300:
                continue
            print(f"Response: {precedence.json()}")
            if precedence.json()['error'] ==  'این کاربر قبلاً در این شرکت به عنوان سهامدار ثبت شده است':
                continue
            break
    

    def tle_precedence_pay(self):
        precedence = requests.get(self.API_URL + 'stock_affairs/precedence/', headers=self.headers)
        precedence = pd.DataFrame(precedence.json())
        users = requests.get(self.API_URL + 'users/', headers=self.headers)
        users = pd.DataFrame(users.json())
        collection = self.database['PriorityPay'].find({"symbol":"fevisa","capDate":"1403/07/28"})
        collection_precedence = self.database['Priority'].find({"symbol":"fevisa","dateInt":14030728})
        
        precedence_list = list(collection_precedence)
        
        for item in collection:
            matching_precedence = next((p for p in precedence_list if p['نام و نام خانوادگی'] == item['frm']), None)
            
            if matching_precedence:
                
                self.database['PriorityPay'].update_one(
                    {"_id": item['_id']},
                    {"$set": {"کد ملی": matching_precedence['کد ملی']}},

                )
                print(item)
                # حق تقدم ها رو بررسی کنیم و بعد ثبت مدل  

        

if __name__ == "__main__":
    mongo_client = Tle()
    # mongo_client.tle_sejam()
    # mongo_client.tle_shareholders()
    # mongo_client.tle_precedence()
    # mongo_client.tle_precedence_pay()
    



