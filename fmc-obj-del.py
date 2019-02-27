#!/usr/bin/python
# =====================================================================================================================
#
# Overview: This script delete objects out of Cisco FMC utilizing the built-in API
#
# Usage:    Run python <script_name> 
#
# Use script at you own risk, and no warranties are inferred or granted. 
# =====================================================================================================================
import requests
import getpass
import json
import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.basicConfig(filename='response.log',level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.INFO)
requests_log.propagate = True

print ("======================================")
print ("=      Cisco Firepower API           =")
print ("=      Object Delete script          =")
print ("=  Will only delete unused objects   =")
print ("=     Use at your own Risk!          =")
print ("======================================")

# Interactive Input of FMC and login
user1= input("Enter your FMC api username: ")
pass1= getpass.getpass(prompt="Enter your FMC password: ")
ipaddr= input("Enter the IP address of Firepower Management Center: ")


url = "https://%s/api/fmc_platform/v1/auth/generatetoken" % ipaddr

results=[]

headers = {
    'cache-control': "no-cache",
    'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
    }

response = requests.request("POST", url, headers=headers, auth=(user1,pass1), verify=False)

# Authenicates token used in additional HTTPS CRUD request
auth = response.headers['X-auth-access-token']

def obj2del(fmcobj):
    url = "https://%s/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/%s" % (ipaddr, fmcobj)

    querystring = {"limit":"1000"}

    headers = {
        'x-auth-access-token': auth,
        'cache-control': "no-cache",
        'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
        }

    # get all objects type based in user reponse from FMC 
    response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
    results=[]
    raw = response.json()
    offset = 0
    p = 0

    if raw['paging']['pages'] == 0:
        for pages in range(p):
            querystring = {"offset":"%d" % offset,"limit":"1000"}
            response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
            offset += 1000
            raw=response.json()
            #print [raw[i] for i in raw.keys()]
            #print raw['items'][1]['name']
            #print [raw[i][0][0].get('name') for i in raw.keys()]
            for i in raw['items']:  
                results.append(i)

    else:
        p=raw['paging']['pages']
        # FMC get all objects for user specified type
        for pages in range(p):
            querystring = {"offset":"%d" % offset,"limit":"1000"}
            response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
            offset += 1000
            raw=response.json()
            #print [raw[i] for i in raw.keys()]
            #print raw['items'][1]['name']
            #print [raw[i][0][0].get('name') for i in raw.keys()]
            for i in raw['items']:  
                results.append(i)
    #test of results link
    #for i in results:
    #   print i['links']['self']

    # Delete objects
    delobj(results)


def delobj(obj):

    global response
    global headers
    global ipaddr
    global user1
    global pass1
    netdel = response 
        
    for id in obj:
            
            #Sends a delete http for all network objects, but only deletes unused objects

            if netdel.status_code != 401:
                #print id['links']['self'] 
                url = id['links']['self']
                netdel = requests.request("DELETE", url, headers=headers, verify=False)
                print (id['name'], netdel)
                logging.info("%s Response: Status code: %d" % (id['name'], netdel.status_code))
            
            else:
                urlauth = "https://%s/api/fmc_platform/v1/auth/generatetoken" % ipaddr
                headers = {
                'cache-control': "no-cache",
                'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
                }
                response = requests.request("POST", urlauth, headers=headers, auth=(user1,pass1), verify=False)
                # Authenicates token used in addiotnal HTTPS CRUD request
                auth = response.headers['X-auth-access-token']
                headers = {
                'x-auth-access-token': auth,
                'cache-control': "no-cache",
                'postman-token': "ff30c506-4739-9d4d-2e53-0dc7efc2036a"
                }  
                
                netdel.status_code = 200
                

# Show Menu
print ("Enter the object type to delete?")
print ("1. networks")
print ("2. ports")
print ("3. hosts")
print ("4. network groups")
print ("5. port groups")
print ("6. address ranges")
print ("7. everything")

while True:
        try:
            question = int(input('Options (1-7),?'))
            
        except ValueError:
            print("Sorry, that is an invaild option.")
            #better try again... Return to the start of the loop
            continue

        if question == 1:
            obj2del('networks')
            break

        elif question == 2:
            obj2del('ports')
            break

        elif question == 3:
            obj2del('hosts')
            break

        elif question == 4:
            obj2del('networkgroups')
            break   

        elif question == 5:
            obj2del('portobjectgroups')
            break   

        elif question == 6:
            obj2del('ranges')
            break   
        
        elif question == 7:
            obj2del('ranges')
            obj2del('portobjectgroups')
            obj2del('networkgroups')
            obj2del('hosts')
            obj2del('ports')
            obj2del('networks')
            break   

        else:
            print('That\'s not an option!')
            continue

