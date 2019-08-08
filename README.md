### Python script for update/set certificate (BYOC) in CDN custom domain by Azure REST API

It's a simple script to use after importing certificate to KeyValut.
Script requires Password and ApplictionID with permissions to list and get certificates in Your KeyValut. You should be aware that the same AppicationId should have permision to CDN endpoint (for example role [CDN Endpoint Contributor](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#cdn-endpoint-contributor). See [more](https://docs.microsoft.com/en-us/cli/azure/ad/sp?view=azure-cli-latest#az_ad_sp_create_for_rbac) at microsoft documentation.  

#####environment settings
```html
export AZUREKV_KEYVAULTNAME="kvname"
export AZUREKV_CERTIFICATENAME="certname"
export AZUREKV_RESOURCEGROUP="kvrg"
export AZURECDN_RESOURCEGROUP="cdnrg"
export AZURECDN_PROFILE="cdnprofile"
export AZURECDN_ENDPOINT="cdnendpoin"
export AZURECDN_CUSTOMDOMAIN="mycustomdomain-com"
export AZUREDNS_SUBSCRIPTIONID="12345678-9abc-def0-1234-567890abcdef"
export AZUREDNS_TENANTID="11111111-2222-3333-4444-555555555555"
export AZUREDNS_APPID="3b5033b5-7a66-43a5-b3b9-a36b9e7c25ed"          # appid of the service principal
export AZUREDNS_CLIENTSECRET="1b0224ef-34d4-5af9-110f-77f527d561bd"   # password from creating the service principal
```
It was tested with CDN Veriozon, python 2.7 and python 3.6 as renew-hook of [acme.sh](https://github.com/Neilpang/acme.sh/wiki/How-to-use-Azure-DNS) wildcard request (AZ CLI also required for renew-hook). 
#####source of renew hook in acme.sh
```html
acme.sh --toPkcs -d "mycustomdomain.com" -d "*.mycustomdomain.com" --password nice-password
az keyvault certificate import --file mycustomdomain.com.pfx --name cert-name-in-kv --vault-name Vault-Name --password nice-password
python3.6 /root/.acme.sh/mycustomdomain.com/start-byoc.py```



