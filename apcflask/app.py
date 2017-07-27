from flask import Flask, render_template, request
import webbrowser
import os
import shutil 
import requests
import sys 
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('dropdown.html')


@app.route('/table',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      resource = request.form['resource']
      getresources(resource)
      return render_template('table.html')
      

domain = os.environ.get('APC_CLUSTER_DOMAIN')
scheme = os.environ.get('APCERA_PROTO')
auth_url = scheme+"://basicauth."+domain+"/v1/oauth2/token"
auth_url2 = scheme+"://api."+domain+"/v1/"

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
    url = auth_url
    headers = { 'authorization': "Basic YWRtaW46UGFzc3cwcmQjMTIzNA==",
    'cache-control': "no-cache"
    }
    
    #Get access token 
    response0 = requests.request("POST", url, headers=headers)
    response = str(response0.text) 
    atindx = response.find("access_token")
    tokentypeindx = response.find("token_type")
    accesstoken = response[atindx + 15: tokentypeindx -3]
    #print("Acess Token: " + accesstoken)
            
    
    #Get a list of resources and append all "fqn" entries to a list; check whether argument is a job
    fqnlist = []
    get = "GET"
    options = ["stager", "app", "gateway", "docker", "sempipe", "capsule"]
    headers = {'authorization': "Bearer " + accesstoken}
    checkjob = False 

    if resource == "sempipe":
        checkjob = True
        customurl = auth_url2 +"jobs?tag=pipeline"
        parsetolist(get,customurl,headers, fqnlist)
    elif resource == "capsule":
        checkjob = True
        ender = "heavy"
        customurl = auth_url2 +"jobs?tag=heavy"
        parsetolist(get,customurl,headers, fqnlist)
    elif resource in options[0:5]:
        checkjob = True
        customurl = auth_url2 +"jobs?tag="+resource
        parsetolist(get,customurl,headers, fqnlist)
    else:
        checkjob = False
        customurl = auth_url2 + resource
        parsetolist(get,customurl,headers, fqnlist)

    #Return a list with only job entries
    list = []
    counter = 0 
    for entry in fqnlist:
        if resource[-1] == 's':
            if resource[:-1] in entry:
                list.append(entry)
                counter = counter + 1 
        else:
            if resource in options and "job" in entry:
                list.append(entry)
                counter = counter + 1
            elif resource not in options and resource in entry:
                list.append(entry)
                counter = counter + 1
    
    #Print cleaned names on newline
    l1 = []
    for x in list:
        resources = x[1:-2]
        #print(resources)
        l1.append(resources)
          
    
    #if resource[-1] == "s":
        #print("There are " + str(counter) + " " + resource)
    #else:
        #print("There are " + str(counter) + " " + resource + "s")
    
    
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
    path = os.path.abspath(os.path.join('templates', 'table.html'))
    
    if len(table) == 0:
        html = "No resources of this kind"
        fp=open(path,'w')
        fp.write(html)
    adder = ""
    for list in table:
        uno = "<td>" + str(list[0]) + "</td>"
        dos = "<td>" + str(list[1]) + "</td>"
        tres = "<td>" + str(list[2]) + "</td>"
        strcol = "<td>" + resource + "</td>"
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
            fp=open(path,'w')
            fp.write(html)
           
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
            fp=open(path,'w')
            fp.write(html)
        
            
   

if __name__ == '__main__':
    webbrowser.open_new('http://localhost:5000') 
    app.run(debug = True, use_reloader= False)
    
  
   