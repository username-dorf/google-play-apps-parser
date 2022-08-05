from google_play_scraper import app
from urllib import response

import xlsxwriter
import requests
import os 


def parse_single(package):
    return app(package)

def filter_single(parsed):
    return [parsed['appId'], parsed['title'], parsed['genre'],  parsed['installs'], parsed['released']]

def get_app_folder(parsed):
    app_folder='apps_content/'+parsed['title']
    if not os.path.exists(app_folder):
        os.mkdir(app_folder)
    return app_folder

def request_ico(parsed):
    response = requests.get(parsed['icon'])
    app_folder=get_app_folder(parsed)
    path=app_folder+'/icon.png'
    open(path,'wb').write(response.content)

def request_screenshots(parsed):
    app_folder=get_app_folder(parsed)
    links=parsed['screenshots']
    sceenshot_amount=3
    if len(links)<sceenshot_amount:
        sceenshot_amount=len(links)
    for index in range(sceenshot_amount):
        response=requests.get(links[index])
        path=(app_folder+'/screenshot{}.png').format(index)
        open(path,'wb').write(response.content)


def write_to_xlsx(rows):
    file_name='apps.xlsx'
    if os.path.exists(file_name):
        os.remove(file_name)

    headers=['App ID', "Title", "Genre", "Installs", "Release Date"]
    data=[]
    data.insert(0,headers)
    for row in rows:
        data.append(row)

    print(data)
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet("Apps")
    row=1
    col=1
    for i in range(len(data)):
        for j in range(len(data[i])):
            worksheet.write(row+i,col+j,data[i][j])        
        row=i+1
    workbook.close()


def main():
    parsed=parse_single('games.urmobi.merge.connect')
    filtred=filter_single(parsed)
    request_ico(parsed)
    request_screenshots(parsed)
    write_to_xlsx([filtred,])
    print(filtred)

if __name__ == "__main__":
    main()

