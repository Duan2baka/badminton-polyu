from turtle import home
from bs4 import BeautifulSoup
import requests
import datetime
import http.cookiejar as cookielib
from constants.userinfo import *
from constants.urls import *
from constants.headers import *
from debug import *

gsmSession = requests.Session()

gsmSession.cookies = cookielib.LWPCookieJar(filename = "./tmp/gsmCookies.txt")



def getLogin_csrf():
    #print("start getting csrf")  
    if DEBUG: responseRes = gsmSession.get(login_home_url,headers = login_header, proxies = proxies, verify=False)
    else: responseRes = gsmSession.get(login_home_url,headers = login_header)
    soup_Res = BeautifulSoup(responseRes.text,'lxml')
    data_Res = soup_Res.find_all('input',{'name':'CSRFToken'})
    CSRFToken = data_Res[0]['value']
    if responseRes.status_code == 200:
        print("Successfully get CSRFToken! CSRFToken = "+ CSRFToken)
    return CSRFToken

def gsmLogin(account, password):    
    
    CSRFToken = getLogin_csrf()

    print("Start logining in...")

    postData = {
        'otheruser': 'N',
        "j_username": account,
        "j_password": password,    
        'buttonAction': 'loginButton',
        "CSRFToken": CSRFToken
    }
    if DEBUG:
        responseRes = gsmSession.post(login_url, data = postData, headers = login_header, proxies=proxies, verify=False, allow_redirects=False)
        responseRes = gsmSession.get(home_url, headers = login_header, proxies=proxies, verify=False)
    else:
        responseRes = gsmSession.post(login_url, data = postData, headers = login_header, allow_redirects=False)
        responseRes = gsmSession.get(home_url, headers = login_header)
    #print(gsmSession.cookies)
    if responseRes.status_code == 200:
        print(f"Successfully log in!")
    #print(responseRes.headers)
    #print(gsmSession.cookies)

    #print_info(responseRes, 'login_res.html')
    gsmSession.cookies.save()
    return CSRFToken

def login():
    CSRFToken = gsmLogin(account, password)
    # print(CSRFToken)
    return gsmSession, CSRFToken