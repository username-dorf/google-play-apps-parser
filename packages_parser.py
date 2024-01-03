import re
from google_play_scraper import app
import xlsxwriter
import requests
import os

FILE_NAME = "apps.xlsx"

SETUP = [
    ("Icon", 10, False),  # text, width, wrap
    ('App ID', 40, False),
    ("Title", 40, False),
    ("Genre", 10, False),
    ("Installs", 15, False),
    ("Release Date", 15, False),
    ("Url", 15, True),
]

ALERT = "Warning: This table is auto-generated. Any changes made will be overridden."


def parse_single(package):
    return app(package, lang='en', country='us')


def filter_single(parsed):
    return [parsed['appId'], parsed['title'], parsed['genre'], parsed['installs'], parsed['released'], parsed['url']]


def get_app_folder(parsed):
    sanitized_directory_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', parsed['title'])
    if sanitized_directory_name.startswith('.'):
        sanitized_directory_name = '_' + sanitized_directory_name[1:]
    app_folder = 'apps_content/' + sanitized_directory_name
    if not os.path.exists(app_folder):
        os.mkdir(app_folder)
    return app_folder


def request_ico(parsed):
    response = requests.get(parsed['icon'])
    app_folder = get_app_folder(parsed)
    path = app_folder + '/icon.png'
    open(path, 'wb').write(response.content)
    return path


def request_screenshots(parsed):
    app_folder = get_app_folder(parsed)
    links = parsed['screenshots']
    screenshot_amount = 3
    screenshot_list = []
    if len(links) < screenshot_amount:
        screenshot_amount = len(links)
    for index in range(screenshot_amount):
        response = requests.get(links[index])
        path = (app_folder + '/screenshot{}.png').format(index)
        open(path, 'wb').write(response.content)
        screenshot_list.append(path)
    return screenshot_list


def get_bold_format(workbook):
    return workbook.add_format({'bold': True})


def get_wrap_format(workbook):
    return workbook.add_format({'text_wrap': True})


def format_column(worksheet):
    for i in range(len(SETUP)):
        worksheet.set_column(i, i, SETUP[i][1])


def write_alert(workbook, worksheet):
    alert_text = ALERT
    worksheet.write(0, 0, alert_text, get_bold_format(workbook))


def write_headers(workbook, worksheet):
    headers = [item[0] for item in SETUP]
    for i in range(len(headers)):
        worksheet.write(1, i, headers[i], get_bold_format(workbook))


def write_to_xlsx(icon_path, rows, workbook, worksheet, row):
    text_format = workbook.add_format({'text_wrap': True})
    write_alert(workbook, worksheet)
    write_headers(workbook, worksheet)
    col = 1
    for i in range(len(rows)):
        worksheet.insert_image(row + i, col-1, icon_path, {"x_scale": 0.1, "y_scale": 0.1})
        for j in range(len(rows[i])):
            worksheet.write(row + i, col + j, rows[i][j], text_format)


def write_screenshots(screenshots_path_array, rows, worksheet, row):
    col = 1
    for i in range(len(rows)):
        for j in range(len(screenshots_path_array)):
            worksheet.insert_image(row + i, col + len(rows[i])+j*2, screenshots_path_array[j],
                                   {"x_scale": 0.4, "y_scale": 0.4})


def create_workbook(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    workbook = xlsxwriter.Workbook(file_name)
    return workbook


def create_worksheet(workbook):
    worksheet = workbook.add_worksheet("Apps")
    return worksheet


def try_create_record(package, workbook, worksheet, package_index):
    try:
        parsed = parse_single(package)
        filtered = filter_single(parsed)
        icon_path = request_ico(parsed)
        screenshot_paths = request_screenshots(parsed)
        alert_spacing = 1
        headers_spacing = 1
        row = package_index + alert_spacing + headers_spacing
        worksheet.set_row(row, 160)
        write_to_xlsx(icon_path, [filtered, ], workbook, worksheet, row)
        write_screenshots(screenshot_paths, [filtered, ], worksheet, row)
        print(filtered)
        return True
    except Exception as e:
        print(f"An exception occurred while parsing {package}\n.{e}")
        return False


def parse_packages(packages):
    file_name = FILE_NAME
    workbook = create_workbook(file_name)
    worksheet = create_worksheet(workbook)
    format_column(worksheet)
    invalid_packages_count = 0
    for index, package in enumerate(packages):
        package_index = index-invalid_packages_count
        record_created = try_create_record(package, workbook, worksheet, package_index)
        if not record_created:
            invalid_packages_count += 1
    workbook.close()
