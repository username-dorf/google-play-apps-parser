import re
from google_play_scraper import app as gapp
from apple_store_parser import parse_apple, apple_to_row, normalize_track_id
import xlsxwriter
import requests
import os
from datetime import datetime


FILE_NAME = "apps.xlsx"
CONTENT_DIRECTORY = "apps_content"

SETUP = [
    ("Icon", 10, False),
    ("Google App ID", 40, False),
    ("Apple Track ID", 20, False),
    ("Title", 40, False),
    ("Genre", 14, False),
    ("Installs", 15, False),
    ("Release Date", 15, False),
    ("Google Url", 20, True),
    ("Apple Url", 20, True),
]

ALERT = "Warning: This table is auto-generated. Any changes made will be overridden."


def parse_single(package):
    return gapp(package, lang='en', country='us')


def filter_google(parsed):
    return {
        "google_id": parsed.get("appId", ""),
        "title": parsed.get("title", ""),
        "genre": parsed.get("genre", ""),
        "installs": parsed.get("installs", ""),
        "release_date": parsed.get("released", ""),
        "google_url": parsed.get("url", ""),
        "icon": parsed.get("icon", ""),
        "screenshots": parsed.get("screenshots", []) or []
    }



def create_content_dir():
    content_directory = CONTENT_DIRECTORY
    if not os.path.exists(f"./{content_directory}"):
        os.makedirs(f"./{content_directory}")


def get_app_folder(parsed):
    sanitized_directory_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', parsed['title'])
    if sanitized_directory_name.startswith('.'):
        sanitized_directory_name = '_' + sanitized_directory_name[1:]
    content_directory = CONTENT_DIRECTORY
    app_folder = f'{content_directory}/{sanitized_directory_name}'
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
    base_col = 1 + len(rows[0])
    for i in range(len(rows)):
        for j, p in enumerate(screenshots_path_array):
            worksheet.insert_image(row + i, base_col + j, p, {"x_scale": 0.4, "y_scale": 0.4})


def create_workbook(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    workbook = xlsxwriter.Workbook(file_name)
    return workbook


def create_worksheet(workbook):
    worksheet = workbook.add_worksheet("Apps")
    return worksheet


def parse_google(package):
    return gapp(package, lang="en", country="us")

def build_row(google_data: dict, apple_data: dict):
    title = (google_data or {}).get("title") or (apple_data or {}).get("title") or ""
    genre = (google_data or {}).get("genre") or (apple_data or {}).get("genre") or ""
    release_raw = (google_data or {}).get("release_date") or (apple_data or {}).get("release_date") or ""
    release = to_iso_date(release_raw)
    installs = (google_data or {}).get("installs") or ""

    return [
        (google_data or {}).get("google_id", ""),
        (apple_data or {}).get("apple_id", ""),
        title,
        genre,
        installs,
        release,
        (google_data or {}).get("google_url", ""),
        (apple_data or {}).get("url", ""),
    ]

def try_create_record(entry, workbook, worksheet, row):
    google_id = entry.get("google", "")
    apple_id = normalize_track_id(entry.get("apple", ""))

    google_data = None
    apple_data = None

    # 1) Google
    if google_id:
        try:
            g = parse_google(google_id)
            google_data = filter_google(g)
        except Exception as e:
            print(f"Google parse failed: {google_id}: {e}")

    # 2) Apple
    if apple_id:
        try:
            a = parse_apple(apple_id, country="us", lang="en")
            apple_data = apple_to_row(a)
        except Exception as e:
            print(f"Apple parse failed: {apple_id}: {e}")

    if not google_data and not apple_data:
        return False

    key = get_record_key(
        (google_data or {}).get("google_id", ""),
        (apple_data or {}).get("apple_id", ""),
    )

    icon_url = (google_data or {}).get("icon") or (apple_data or {}).get("icon") or ""
    screenshots = (google_data or {}).get("screenshots") or (apple_data or {}).get("screenshots") or []

    icon_path, screenshot_paths = request_icon_and_screens(key, icon_url, screenshots)

    worksheet.set_row(row, 160)
    data_row = build_row(google_data, apple_data)

    write_to_xlsx(icon_path, [data_row], workbook, worksheet, row)
    write_screenshots(screenshot_paths, [data_row], worksheet, row)

    print(data_row)
    return True


def get_record_key(google_id: str, apple_id: str):
    if google_id:
        return google_id
    if apple_id:
        return f"apple_{apple_id}"
    return "unknown"


def get_app_folder_by_key(key: str):
    app_folder = f"{CONTENT_DIRECTORY}/{key}"
    if not os.path.exists(app_folder):
        os.makedirs(app_folder, exist_ok=True)
    return app_folder


def download_file(url: str, path: str):
    if not url:
        return False
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return True


def request_icon_and_screens(key: str, icon_url: str, screenshots: list, max_shots=3):
    folder = get_app_folder_by_key(key)

    icon_path = f"{folder}/icon.png"
    if icon_url:
        download_file(icon_url, icon_path)

    shot_paths = []
    for i, u in enumerate((screenshots or [])[:max_shots]):
        p = f"{folder}/screenshot{i}.png"
        download_file(u, p)
        shot_paths.append(p)

    return icon_path, shot_paths


def parse_entries(entries):
    file_name = FILE_NAME
    workbook = create_workbook(file_name)
    worksheet = create_worksheet(workbook)

    format_column(worksheet)
    create_content_dir()

    invalid_count = 0
    alert_spacing = 1
    headers_spacing = 1

    for index, entry in enumerate(entries):
        package_index = index - invalid_count
        row = package_index + alert_spacing + headers_spacing  # xlsxwriter row index (0-based)
        ok = try_create_record(entry, workbook, worksheet, row)
        if not ok:
            invalid_count += 1

    workbook.close()


def parse_packages(packages):
    # backward compatible: google-only list[str]
    entries = [{"google": p, "apple": ""} for p in packages]
    parse_entries(entries)


def to_iso_date(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip()
    if "T" in s and len(s) >= 10:
        s = s[:10]

    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except:
        pass

    try:
        dt = datetime.strptime(s, "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        pass

    return s


