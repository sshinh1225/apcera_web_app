import requests
import sys 
import json
import os

#searches json for "fqn" keyword and appends to a list for further filtering
def parsetolist(get, customurl, headers, fqnlist):
    response = requests.request("GET", customurl, headers=headers)
    x = response.json()
    data = (str(json.dumps(x))).split()
    for word in range(len(data)):
        if "fqn" in data[word] and "_fqn" not in data[word]:
            fqnlist.append(data[word+1])
      
def getresources(resource): 
    #Local variables for function 
    arg = sys.argv[1]
    arg_str  = str(arg)
    url = "http://basicauth.dev.wgcloud.net/v1/oauth2/token"
    headers = { 'authorization': "Basic YWRtaW46UGFzc3cwcmQjMTIzNA==",
    'cache-control': "no-cache"
    }
    
    #Get access token 
    response0 = requests.request("POST", url, headers=headers)
    response = str(response0.text) 
    atindx = response.find("access_token")
    tokentypeindx = response.find("token_type")
    accesstoken = response[atindx + 15: tokentypeindx -3]
    print("Acess Token: " + accesstoken)
            
    
    #Get a list of resources and append all "fqn" entries to a list; check whether argument is a job
    fqnlist = []
    get = "GET"
    options = ["stager", "app", "gateway", "docker", "sempipe", "capsule"]
    headers = {'authorization': "Bearer " + accesstoken}
    checkjob = False 
    try: 
        if arg_str == "sempipe":
            checkjob = True 
            customurl = "http://api.dev.wgcloud.net/v1/jobs?tag=pipeline"
            parsetolist(get,customurl,headers, fqnlist)
        elif arg_str == "capsule":
            checkjob = True 
            ender = "heavy"
            customurl = "http://api.dev.wgcloud.net/v1/jobs?tag=heavy" 
            parsetolist(get,customurl,headers, fqnlist)
        elif arg_str in options[0:5]:
            checkjob = True 
            customurl = "http://api.dev.wgcloud.net/v1/jobs?tag=" + arg_str
            parsetolist(get,customurl,headers, fqnlist)
        else:
            checkjob = False 
            customurl = "http://api.dev.wgcloud.net/v1/" + arg_str
            parsetolist(get,customurl,headers, fqnlist)
    except:
        print("Valid names: app, stager, gateway, sempipe, capsule, docker, jobs, packages, networks, services, providers")

    
    #Return a list with only job entries
    list = []
    counter = 0 
    for entry in fqnlist:
        if arg_str[-1] == 's':
            if arg_str[:-1] in entry:
                list.append(entry)
                counter = counter + 1 
        else:
            if arg_str in options and "job" in entry:
                list.append(entry)
                counter = counter + 1
            elif arg_str not in options and arg_str in entry:
                list.append(entry)
                counter = counter + 1
    
    #Print cleaned names on newline
    l1 = []
    for x in list:
        resources = x[1:-2]
        print(resources)
        l1.append(resources)
          
    
    if arg_str[-1] == "s":
        print("There are " + str(counter) + " " + arg_str)
    else:
        print("There are " + str(counter) + " " + arg_str + "s")
    
    #splice returned results into three categories: Realm, Namespace, Name
    table = []
    for i in l1:
        nested = []
        findx = i.find("::")
        first = i[:findx]
        nested.append(first)
        string2 = i[findx+2:]
        sindx = string2.find("::")
        second = string2[:sindx]
        nested.append(second)
        third = string2[sindx + 2 :]
        nested.append(third)
        table.append(nested)
    table_str = str(table)

    #format return as a table (specifically, striped rows and header)
    css = """<html>
    <head>
    <style>
    table {
    border-collapse: collapse;
    width: 100%;
    }
    th, td {
    text-align: left;
    padding: 8px;
    }
    tr:nth-child(even){background-color: #f2f2f2}
    </style>
    </head>
    <body>

    <h2>Apcera Resources</h2> """
    
    #prompts user to generate html or terminate program 
    query = raw_input("Generate HTML page? Y/N: ")
    if query == "Y" or query == "y":
        adder = ""
        for list in table:
            uno = "<td>" + str(list[0]) + "</td>"
            dos = "<td>" + str(list[1]) + "</td>"
            tres = "<td>" + str(list[2]) + "</td>"
            strcol = "<td>" + arg_str + "</td>"
            if checkjob == False:
                adder = adder + "<tr>" + uno + dos + tres + "</tr>"
                html =css + " " + """  <table border = "1" cellpadding = "5" cellspacing = "5">
                <thead>
                  <tr>
                  <th>Realm</th>
                  <th>Namespace</th>
                  <th>Name</th>
                </tr>
                </thead>
                <tbody>""" + adder + " </tbody> </table>"
            elif checkjob == True:
                adder = adder + "<tr>" + uno + strcol + dos + tres + "</tr>"
                html = css + " " + """ <table border = "1" cellpadding = "5" cellspacing = "5"> <thead>
                  <tr>
                  <th>Realm</th>
                  <th>Type</th>
                  <th>Namespace</th>
                  <th>Name</th>
                </tr>
                </thead>
                <tbody>""" + adder + " </tbody> </table>"
        f = open('table.html', 'w')
        f.write(html)
        os.startfile('table.html')
    else:
       sys.exit()
    

if __name__ == "__main__":
    if len(sys.argv) == 2:
        getresources(sys.argv[1])
    else:
        sys.exit("1 argument needed")            



        
