from constants.userinfo import *
from constants.headers import *
from constants.urls import *
from debug import *
from bs4 import BeautifulSoup
import datetime
import time
import re

#book_url = 'https://www40.polyu.edu.hk/starspossfbstud/secure/ui_make_book/make_book.do'

def getBook_csrf(session):
    # print("start getting new csrf")  
    if DEBUG: responseRes = session.get(make_book_url,headers = login_header, proxies = proxies, verify=False)
    else: responseRes = session.get(make_book_url,headers = login_header)
    soup_Res = BeautifulSoup(responseRes.text,'lxml')
    data_Res = soup_Res.find_all('input',{'name':'CSRFToken'})
    # print(soup_Res)
    CSRFToken = data_Res[0]['value']
    if responseRes.status_code == 200: print("Successfully get new CSRFToken for booking, CSRFToken = "+ CSRFToken)
    return CSRFToken

def parse_string(input_str):
    confirmed = False # judge whether a reservation was made before at this day
    #print(input_str)
    #exit(0)
    # get the start location of time information
    posL = re.search('timeSlotColumns', input_str, flags=0).span()[1] + 2
    posR = re.search('jscCutOffDateTime', input_str, flags=0).span()[0] - 2
    str = input_str[posL : posR]
    #print_to_file(str, 'str.txt')
    it = re.finditer('title', str)
    
    title_pos = [] # store position of every 'title' phase 
    for i in it: title_pos.append(i.span()[1])
    title_pos.append(len(str))
    date_table = []
    pre = 0
    flag = False
    for i in title_pos: # divide data by court
        if flag == False:
            flag = True
            pre = i 
            continue
        court_name = str[pre + 3 : re.search('"', str[pre + 4 : i]).span()[0] + pre + 4]
        #print(court_name)
        it = re.finditer('fromDateTime', str[pre : i])
        time_pos = []
        for j in it: time_pos.append(j.span()[1] + pre)
        time_pos.append(i)
        facility_table = []
        pre1 = 0
        flag1 = False
        for j in time_pos: # divide data by time
            if flag1 == False:
                flag1 = True
                pre1 = j
                continue
            fromTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str[pre1 + 2 : pre1 + 15])/1000))
            endTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str[pre1 + 29 : pre1 + 42])/1000))

            fee = int(str[re.search('"charge":', str[pre1 : j]).span()[1] + pre1 : re.search('"rfndRsvFee"', str[pre1 : j]).span()[0] + pre1 -1])
            availability = (re.search('\d',str[re.search('occupiedFacilityIds',str[pre1 : j]).span()[1] + pre1 : re.search('hasConfirmation',str[pre1 : j]).span()[0] + pre1]) == None)

            confirmed = True if str[re.search('hasConfirmation',str[pre1 : j]).span()[1] + pre1 + 2] == 't' else confirmed

            facility_table.append({'availability' : availability, 'fee' : fee, 'fromTime' : fromTime, 'endTime' : endTime})

            pre1 = j

            #print(f"from: {fromTime} to: {endTime}")

        date_table.append({court_name : facility_table})

        pre = i

    #print(confirmed)
    
    return date_table, confirmed

def get_time_table(session):
    time_table = []
    today = datetime.date.today()

    CSRFToken = getBook_csrf(session) # get new CSRFToken
    if DEBUG: session.get(home_url, headers = get_header, proxies=proxies, verify=False, allow_redirects=False) # get ltpatoken2 cookie 
    else: session.get(home_url, headers = get_header, allow_redirects=False)
    for i in range(0,7): # system allows user to book at most 7 days advance
        postData = {
            "CSRFToken": CSRFToken,
            'fbUserId': fbUserId, #fbUserId seems to be able to get from html... I will optimize this later
            "bookType": 'INDV',
            "dataSetId": '18',
            "actvId": '2', 
            'searchDate': (today + datetime.timedelta(days = i)).strftime('%d %b %Y'),
            "ctrId": '', 
            "facilityId": '', 
            "showCourtAreaDetails": 'true'
        }
        book_url = 'https://www40.polyu.edu.hk/starspossfbns/secure/ui_make_book/timetable.json?CSRFToken=' + CSRFToken
        print(f'Start posting data to {book_url}')
        if DEBUG: responseRes = session.post(book_url, headers=book_header, data = postData, proxies=proxies, verify=False)
        else: responseRes = session.post(book_url, headers=book_header, data = postData)

        if responseRes.status_code == 200: print(f"Successfully get booking timetable on {(today + datetime.timedelta(days = i)).strftime('%d %b %Y')}!")
        #print_info(responseRes, 'book_res.html')

        time_table.append(parse_string(responseRes.text)) # parse received data
    
    return time_table, CSRFToken


if __name__ == "__main__": # DEBUG
    f=open('./result/book_res.html')
    str=f.read()
    #get_time_table()
    parse_string(str)
    f.close()
    