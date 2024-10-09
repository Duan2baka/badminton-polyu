from bs4 import BeautifulSoup

def print_info(responseRes, file):
    f = open(file,'w')
    soup_Res = BeautifulSoup(responseRes.text,'lxml')
    print(soup_Res.encode("gbk", 'ignore').decode("gbk", "ignore"),file=f)
    f.close()

def print_to_file(text, file):
    f = open(file, 'w')
    print(text,file=f)
    f.close()