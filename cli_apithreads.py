import json
import requests
import sys
from colorama import Fore
import threading
from requests.exceptions import HTTPError
import datetime
import time

totalPass=0
totalFail=0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def createID(thread):
    value=str(thread)+"_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+str(time.time()*1000)[0:4]
    return str(value)

def arguments():
    data={
        "method":"GET",
        "bodyData":"",
        "url":"",
        "resCode":"200",
        "threads":"1",
        "headers":"",
        "delay":"0",
        "assertion":"",
        "type":"json"
        }
    arguments=sys.argv
    for i in range(len(arguments)):
        if arguments[i]=="-method":
            data["method"]=arguments[i+1]
        elif arguments[i]=="-bodyData":
            data["bodyData"]=arguments[i+1]
        elif arguments[i]=="-headers":
            data["headers"]=arguments[i+1]
        elif arguments[i]=="-url":
            data["url"]=arguments[i+1]
        elif arguments[i]=="-resCode":
            data["resCode"]=arguments[i+1]
        elif arguments[i]=="-threads":
            data["threads"]=arguments[i+1]
        elif arguments[i]=="-delay":
            data["delay"]=arguments[i+1]
        elif arguments[i]=="-type":
            data["type"]=arguments[i+1]
                
    return data

def apiGet(url,headers,body,resCode):
    global totalPass
    global totalFail
    headersFile=open(headers,"r")
    headersData=json.load(headersFile)

    try:
        res=requests.get(url,headers=headersData)
        if str(res.status_code) == resCode:
            print(bcolors.OKBLUE + "\nUrl: "+url+"\n"+bcolors.OKCYAN+"Response: "+json.dumps(res.json())+"\n"+bcolors.WARNING+"Elapsed Time: "+str(res.elapsed)+"\n"+bcolors.OKGREEN+"Result: Passed")
            totalPass+=1
        else:
            print(bcolors.OKBLUE + "\nUrl: "+url+"\n"+bcolors.OKCYAN+"Response: "+json.dumps(res.json())+"\n"+bcolors.WARNING+"Elapsed Time: "+str(res.elapsed)+"\nResponse Code: "+str(res.status_code)+"\n"+bcolors.FAIL+"Result: Failed")
            totalFail+=1

    except HTTPError:
        print(bcolors.FAIL+ "HTTP Error "+str(HTTPError)+"\n")
    except Exception as err:
        print(bcolors.FAIL+'Other error occurred: '+str(err)+"\n")

    
def apiPost(url,body,resCode,headers,typeAPI,thread):
    global totalPass
    global totalFail
    try: 
        if typeAPI.lower() =="json":
            jsonFile=open(body,"rb").read()
            value=bytes(createID(thread),"utf-8")
            bodyData=jsonFile.replace(b"${id}",value)
        elif typeAPI.lower() == "xml":
            bodyData=open(body,"rb").read()
            value=bytes(createID(thread),"utf-8")
            bodyData=bodyData.replace(b"${id}",value)
        else:
            raise Exception("Invalid type")
        

        headerFile=open(headers,"r")
        headersData=json.load(headerFile)

        try:
            res= requests.request("POST",url,data=bodyData,headers=headersData)
            if str(res.status_code)==resCode:
                print(bcolors.OKBLUE + "\nUrl: "+url+"\n"+bcolors.OKCYAN+"Response: "+json.dumps(res.json())+bcolors.WARNING+"\nElapsed Time: "+str(res.elapsed)+"\n"+bcolors.OKGREEN+"Result: Passed")
                totalPass+=1
            else:
                print(bcolors.OKBLUE + "\nUrl: "+url+"\n"+bcolors.OKCYAN+"Response: "+json.dumps(res.json())+bcolors.WARNING+"\nElapsed Time: "+str(res.elapsed)+"\nResponse Code: "+str(res.status_code)+"\n"+bcolors.FAIL+"Result: Failed")
                totalFail+=1
        except Exception as err:
            print(bcolors.FAIL+'Other error occurred: '+str(err)+"\n")
            
    except Exception as err:
        print(bcolors.FAIL+'Other error occurred: '+str(err)+"\n")

def tasks(data,thread):
    if data["method"].lower() == "get":
        apiGet(data["url"],resCode=data["resCode"],body=data["bodyData"],headers=data["headers"])
    if data["method"].lower() == "post":
        apiPost(data["url"],resCode=data["resCode"],body=data["bodyData"],headers=data["headers"],typeAPI=data["type"],thread=thread)



value=arguments()
for i in range(int(value["threads"])):
    th=threading.Timer(int(value["delay"]),tasks,args=(value,str(i)))
    th.start()
    th.join()



print(bcolors.BOLD+ bcolors.UNDERLINE+"\n"+"Total Pass: "+str(totalPass)+"/"+str(value["threads"])+" "+"Total Fail: "+str(totalFail)+"/"+str(value["threads"]))
print(Fore.WHITE)