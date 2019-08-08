#!/usr/local/bin/python3.6

import requests
import os
import json

keyvault_name = os.environ['AZUREKV_KEYVAULTNAME']
cert_name = os.environ['AZUREKV_CERTIFICATENAME']
kv_rg = os.environ['AZUREKV_RESOURCEGROUP']
cdn_rg = os.environ['AZURECDN_RESOURCEGROUP']
cdn_profile = os.environ['AZURECDN_PROFILE']
cdn_endpoint = os.environ['AZURECDN_ENDPOINT']
cdn_customdomain = os.environ['AZURECDN_CUSTOMDOMAIN']
#
## Settings borrowed from acme.sh
#
tenant_id = os.environ['AZUREDNS_TENANTID']
subscription_id = os.environ['AZUREDNS_SUBSCRIPTIONID']
client_id = os.environ['AZUREDNS_APPID']
client_secret = os.environ['AZUREDNS_CLIENTSECRET']

resource = 'https://vault.azure.net'
resource_mgmt = 'https://management.azure.com/'
login_authority_url = ('https://login.microsoftonline.com/%s/oauth2/token' % tenant_id)
kv_authority_url = ('https://%s.vault.azure.net/certificates/%s/versions?api-version=7.0' % (keyvault_name, cert_name))
cdn_mgmt_url = ('https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Cdn/profiles/%s/endpoints/%s/customDomains/%s/enableCustomHttps?api-version=2019-04-15' % (subscription_id, cdn_rg, cdn_profile, cdn_endpoint, cdn_customdomain))

#
## Body
#
payload = { 'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': resource,
}
#
## Send first request for token to keyvalut
#
login_auth_response = requests.post(url=login_authority_url, data=payload)
if login_auth_response.status_code == 200:
   data = json.loads(login_auth_response.content)
   #print(data['access_token'])
   header = { 'Authorization' : 'Bearer ' + data['access_token'],
               'Content-Type' : 'application/x-www-form-urlencoded',
   }
   #
   ## Ask API for KeyVault for certificate versions
   #
   kv_auth_response = requests.get(url=kv_authority_url, headers=header)
   if kv_auth_response.status_code == 200:
      data = json.loads(kv_auth_response.content)
      #print(data['value'])
      #
      ## Lets find youngest vesrion of certificate
      #
      if len(data['value']) > 0:
         for x in range(len(data['value'])):
             if x == 0:
                youngest = data['value'][x]['attributes']['exp']
                cert_url = data['value'][x]
             if data['value'][x]['attributes']['exp'] > youngest:
                youngest = data['value'][x]['attributes']['exp']
                cert_url = data['value'][x]
         arry = cert_url['id'].split('/')
         if cert_name != arry[len(arry)-2]:
             print("Error: Certificate name not equal.")
             os._exit(1)
         cert_version = arry[len(arry)-1]
      else:
         print("Error: No certificate found.")
         os._exit(1)
      #
      ## Body
      #
      payload = { 'grant_type': 'client_credentials',
                  'client_id': client_id,
                  'client_secret': client_secret,
                  'resource': resource_mgmt,
      }
      login_auth_response = requests.post(url=login_authority_url, data=payload)
      #
      ## Ask API for new token to CDN
      #
      if login_auth_response.status_code == 200:
         data = json.loads(login_auth_response.content)
         #print(data['access_token'])
         header = { 'Authorization' : 'Bearer ' + data['access_token'],
                    'Content-Type' : 'application/json',
         }
         #
         ## Body
         #
         payload = {
           "certificateSource": "AzureKeyVault",
             "certificateSourceParameters": {
             "@odata.type": "#Microsoft.Azure.Cdn.Models.KeyVaultCertificateSourceParameters",
             "deleteRule": "NoAction",
             "updateRule": "NoAction",
             "resourceGroupName": "%s" % kv_rg,
             "secretName": "%s" % cert_name,
             "secretVersion": "%s" % cert_version,
             "subscriptionId": "%s" % subscription_id,
             "vaultName": "%s" % keyvault_name
           },
           "protocolType": "ServerNameIndication"
         }
         login_auth_response = requests.post(url=cdn_mgmt_url, headers=header ,data=json.dumps(payload))
         print(login_auth_response.text)
         if login_auth_response.status_code == 202:
            print ("Sucess, deploying BYOC in progress.")
            print (login_auth_response.status_code)
         else:
            print ("Error: %s" % login_auth_response.status_code)
            print (login_auth_response.reason)
            os._exit(1)
   else:
      print ("Error: %s" % kv_auth_response.status_code)
      print (kv_auth_response.reason)
      os._exit(1)
else:
   print ("Error: %s" % login_auth_response.status_code)
   print (login_auth_response.reason)
   os._exit(1)
