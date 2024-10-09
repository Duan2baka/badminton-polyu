from get_time_table import get_time_table
from login import login

import urllib3
from urllib3.exceptions import InsecureRequestWarning
    

if __name__ == "__main__":
    urllib3.disable_warnings(InsecureRequestWarning)
    session, LoginCSRFToken = login()
    time_table, BookCSRFToken = get_time_table(session)
    