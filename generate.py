import os
import sys
import json
import re
import copy
import uuid



from datetime import (
    datetime,
    timedelta
)

from moviepy import VideoFileClip



if getattr(sys, "frozen", False):

    APP_DIR = os.path.dirname(
        sys.executable
    )

else:

    APP_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

# ====================================
# تحميل Smart Replacements
# ====================================

def load_replacements():

    replacement_file = os.path.join(
        APP_DIR,
        "_internal",
        "replacements.json"
    )


    if not os.path.exists(
        replacement_file
    ):

        return {}

    with open(
        replacement_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def generate_playlists(
    base,
    month,
    selected_days,
    start_time
):

  

    global BASE
    global month_name
    global playlist_start_time

    global CONTENT_FOLDER
    global ADS_FOLDER
    global INSERTS_FOLDER
    global OUTPUT_FOLDER

    global CATEGORY_FILE
    global CHANNEL_CATEGORY

    global ads_files
    global insert_files
    global SHORTEST_AD_DURATION
    
    global SERIES_HOURS
    global MAX_DELAY
 
    BASE = base
    month_name = month
    playlist_start_time = start_time

    print("START TIME:", playlist_start_time)

    
    # ====================================
    # المسارات
    # ====================================

    CONTENT_FOLDER = os.path.join(
        BASE,
        "Content"
    )

    ADS_FOLDER = os.path.join(
        BASE,
        "Ads"
    )

    INSERTS_FOLDER = os.path.join(
        BASE,
        "Inserts"
    )

    OUTPUT_FOLDER = os.path.join(
        BASE,
        "Schedules"
    )

    # ====================================
    # قراءة اسم الكاتيكوري
    # ====================================

    CATEGORY_FILE = os.path.join(
        BASE,
        "Settings",
        "category.txt"
    )

    CHANNEL_CATEGORY = ""

    if os.path.exists(CATEGORY_FILE):

        with open(
            CATEGORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            CHANNEL_CATEGORY = f.read().strip()

    # ====================================
    # أوقات بداية المسلسلات
    # ====================================

    SERIES_HOURS = [
        16,
        17,
        18,
        19,
        20,
        21
    ]

    # ====================================
    # أقصى تأخير مسموح
    # ====================================

    MAX_DELAY = 10


    ads_files = load_video_files(
        ADS_FOLDER
    )

    insert_files = load_video_files(
        INSERTS_FOLDER
    )

    SHORTEST_AD_DURATION = (
        get_shortest_ad_duration()
    )


    # ====================================
    # قراءة الشهر المحدد
    # ====================================

    month_folder = os.path.join(
        CONTENT_FOLDER,
        month_name
    )

    folders = [

        f for f in os.listdir(month_folder)

        if os.path.isdir(
            os.path.join(month_folder, f)
        )

    ]

    # ====================================
    # استخدام الأيام المحددة من GUI
    # ====================================

   


    folders = selected_days
  

  

    for folder in folders:

        generate_schedule(

            folder,

            os.path.join(
                month_folder,
                folder
            )

        )


   


# ====================================
# كاش مدة الفيديو
# ====================================

duration_cache = {}

# ====================================
# جلب مدة الفيديو
# ====================================

def get_video_duration(path):

    if path in duration_cache:
        return duration_cache[path]

    clip = VideoFileClip(path)

    duration = int(clip.duration)

    clip.close()

    duration_cache[path] = duration

    return duration

# ====================================
# إنشاء عنصر Playlist Native
# ====================================

def create_item(
    template_item,
    index,
    name,
    path,
    start_time,
    duration_seconds,
    category=""
):

    item = copy.deepcopy(
        template_item
    )

    # ====================================
    # تحويل الوقت إلى SMPTE
    # ====================================

    hours = duration_seconds // 3600

    minutes = (duration_seconds % 3600) // 60

    seconds = duration_seconds % 60

    frames = 0

    duration_str = (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d}:"
        f"{frames:02d}"
    )

    # ====================================
    # تحديث البيانات
    # ====================================

    item["index"] = index

    item["Name"] = name

    item["Path"] = path

    item["Category"] = category

    item["StartTime"] = start_time.strftime(
    '%H:%M:%S'
)

    item["FullStartTime"] = start_time.strftime(
        '%Y-%m-%dT%H:%M:%S'
    )

    item["DoubleIn"] = 0.0

    item["DoubleOut"] = float(
        duration_seconds
    )

    item["DoubleDuration"] = float(
        duration_seconds
    )

    item["OriginalDuration"] = float(
        duration_seconds
    )

    item["Duration"] = duration_str

    item["Out"] = duration_str

  

    item["uniquePINumber"] = str(
        uuid.uuid4()
)

    return item
# ====================================
# قراءة ملفات الفيديو
# ====================================

def load_video_files(folder):

    return [

        os.path.join(folder, f)

        for f in os.listdir(folder)

        if f.lower().endswith((
            ".mp4",
            ".mkv",
            ".mov"
        ))

    ]


# ====================================
# أقصر إعلان
# ====================================

def get_shortest_ad():

    shortest_file = None

    shortest_duration = 999999

    for file in ads_files:

        duration = get_video_duration(file)

        if duration < shortest_duration:

            shortest_duration = duration

            shortest_file = file

    return shortest_file, shortest_duration

# ====================================
# أقصر إعلان
# ====================================

def get_shortest_ad_duration():

    shortest = 999999

    for file in ads_files:

        duration = get_video_duration(
            file
        )

        if duration < shortest:

            shortest = duration

    return shortest


# ====================================
# قراءة schedule.txt
# ====================================

def read_schedule_file(folder_path):

    schedule_path = os.path.join(
        folder_path,
        "schedule.txt"
    )

    if not os.path.exists(schedule_path):

        print(f"Missing schedule.txt in {folder_path}")

        return []

    with open(
        schedule_path,
        "r",
        encoding="utf-8"
    ) as f:

        lines = []

        for line in f:

            line = line.strip()

            if not line:

                continue

            if "|" in line:

                slot_type, series_name = line.split(
                    "|",
                    1
                )

            else:

                slot_type = "1 Hour"
                series_name = line

            lines.append({

                "type": slot_type,

                "name": series_name

            })

    return lines

# ====================================
# تحميل Smart Replacements
# ====================================

replacement_file = os.path.join(
    os.path.dirname(__file__),
    "replacements.json"
)



if os.path.exists(replacement_file):

    with open(
        replacement_file,
        "r",
        encoding="utf-8"
    ) as f:

        REPLACEMENTS = json.load(f)

    

else:

    REPLACEMENTS = {}

# ====================================
# استخراج رقم الحلقة
# ====================================

def extract_episode_number(filename):

    match = re.search(
        r"[حhH]\s*(\d+)",
        filename
    )

    if match:

        return int(
            match.group(1)
        )

    return 999999

# ====================================
# البحث عن الحلقة أو الحلقتين
# ====================================

def find_video_files(
    folder_path,
    series_name,
    day_name
):

    matched_files = []

    files = sorted(
        os.listdir(folder_path)
    )


    search_name = series_name



    # ====================================
    # البحث داخل الملفات
    # ====================================



    for file in files:

        if file.lower().endswith((
            ".mp4",
            ".mkv",
            ".mov"
        )):



            if search_name.lower() in file.lower():

                matched_files.append(file)

    matched_files.sort(
        key=extract_episode_number
    )

    # ====================================
    # إذا لكة حلقتين
    # ====================================

    if len(matched_files) >= 2:

        return matched_files[:2]

    # ====================================
    # إذا لكة حلقة وحدة
    # ====================================

    elif len(matched_files) == 1:


        return [matched_files[0]]



    return []

# ====================================
# اختيار أفضل تراك
# ====================================

def find_best_clip(
    files,
    remaining_seconds,
    max_delay,
    last_clip_name
):

    best_file = None

    best_duration = None

    best_diff = 999999

    for file in files:

        current_name = os.path.basename(file)

        # منع التكرار المباشر

        if current_name == last_clip_name:
            continue

        duration = get_video_duration(file)

        delay = duration - remaining_seconds

        diff = abs(delay)

        # تجاهل التأخير الكبير

        if delay > max_delay:
            continue

        # اختيار الأقرب

        if diff < best_diff:

            best_diff = diff

            best_file = file

            best_duration = duration

    return best_file, best_duration


def get_day_number(day):
    return int(day.split("-")[0])


# ====================================
# إنشاء الجدول
# ====================================

def generate_schedule(
    folder_name,
    folder_path
):

    playlist_items = []

    index = 0

    scheduled_series = read_schedule_file(
        folder_path
    )

    current_time = datetime.strptime(
       playlist_start_time + ":00",
       "%H:%M:%S"
    )

    # ====================================
    # تحميل Template MP
    # ====================================

    if getattr(sys, "frozen", False):

        template_file = os.path.join(
            APP_DIR,
            "_internal",
            "template.MP"
        )

    else:

        template_file = os.path.join(
            APP_DIR,
            "template.MP"
        )

    with open(
        template_file,
        "r",
        encoding="utf-8"
    ) as f:

        schedule = json.load(f)

    template_item = schedule[
         "PlaylistItems"
    ][0]
    playlist_items = []

    # ====================================
    # Insert at Playlist Start
    # ====================================

    if insert_files:

        first_insert = insert_files[0]

        insert_duration = get_video_duration(
            first_insert
        )

        insert_name = os.path.splitext(
            os.path.basename(first_insert)
        )[0]

        playlist_items.append(

            create_item(
                template_item,
                index,
                insert_name,
                first_insert,
                current_time,
                insert_duration,
                ""
            )

        )

        index += 1

        current_time += timedelta(
            seconds=insert_duration
        )

        last_was_insert = True


    # ====================================
    # تشغيل المسلسلات
    # ====================================

    replacements = load_replacements() 

    base_hour = int(
        playlist_start_time.split(":")[0]
    )

    slot_target_time = datetime.strptime(
        playlist_start_time + ":00",
        "%H:%M:%S"
    )

    for i, slot in enumerate(scheduled_series):



        series_name = slot["name"]

        slot_type = slot["type"]

        SLOT_SECONDS = {

            "1 Hour": 3600,

            "1.5 Hour": 5400,

            "2 Hours": 7200

        }

        target_duration = SLOT_SECONDS.get(
            slot_type,
            3600
        )

        # ====================================
        # Persistent Replacement System
        # ====================================

        search_name = series_name

        for replacement_day in replacements:

            if get_day_number(replacement_day) <= get_day_number(folder_name):

                if series_name in replacements[
                    replacement_day
                ]:

                    search_name = replacements[

                        replacement_day

                    ][series_name]

        

        target_time = slot_target_time

        # ====================================
        # إضافة الفواصل
        # ====================================

        last_clip_name = ""

       

        while current_time < target_time:

            remaining_seconds = int(
                (target_time - current_time).total_seconds()
            )

            if remaining_seconds <= get_shortest_ad_duration():

                if last_was_insert:

                    best_file, best_duration = find_best_clip(
                        ads_files,
                        remaining_seconds,
                        MAX_DELAY,
                        last_clip_name
                    )

                else:

                    best_file, best_duration = find_best_clip(
                        insert_files,
                        remaining_seconds,
                        MAX_DELAY,
                        last_clip_name
                    )

            else:

                best_file, best_duration = find_best_clip(
                    ads_files,
                    remaining_seconds,
                    MAX_DELAY,
                    last_clip_name
                )

            if not best_file:

                shortest_ad, shortest_duration = (
                    get_shortest_ad()
                )

                if shortest_ad:

                    projected_delay = (
                        shortest_duration
                        - remaining_seconds
                    )

                    if (
                        projected_delay >= 0
                        and projected_delay <= 30
                    ):

                        best_file = shortest_ad

                        best_duration = shortest_duration

                    else:

                        break

                else:

                    break

            clip_name = os.path.splitext(
                os.path.basename(best_file)
            )[0]

            playlist_items.append(

                create_item(
                    template_item,
                    index,
                    clip_name,
                    best_file,
                    current_time,
                    best_duration,
                    ""
                )

            )

            index += 1

            current_time += timedelta(
                seconds=best_duration
            )

            last_clip_name = os.path.basename(
                best_file
            )

            if best_file in insert_files:

                last_was_insert = True

            else:

                last_was_insert = False


        # ====================================
        # منع البدء المبكر
        # ====================================




        if current_time < target_time:

            current_time = target_time



        # ====================================
        # الحلقة أو الحلقتين
        # ====================================


        

        videos = find_video_files(
            folder_path,
            search_name,
            folder_name
        )

        if not videos:

            print(f"Missing series: {series_name}")

            continue

        for video in videos:

            full_video_path = os.path.join(
                folder_path,
                video
            )

            video_duration = get_video_duration(
                full_video_path
            )

            video_name = os.path.splitext(
                video
            )[0]



            playlist_items.append(

                create_item(
                    template_item,
                    index,
                    video_name,
                    full_video_path,
                    current_time,
                    video_duration,
                    CHANNEL_CATEGORY
                )

            )

            index += 1

            current_time += timedelta(
                seconds=video_duration
            )

        slot_target_time += timedelta(
            seconds=target_duration
        )

    # ====================================
    # تكملة الفواصل حتى 22:00
      # ====================================

    start_time = datetime.strptime(
        playlist_start_time + ":00",
        "%H:%M:%S"
    )

    total_seconds = 0

    for slot in scheduled_series:

        if slot["type"] == "1 Hour":

            total_seconds += 3600

        elif slot["type"] == "1.5 Hour":

            total_seconds += 5400

        elif slot["type"] == "2 Hours":

            total_seconds += 7200

    end_time = start_time + timedelta(
        seconds=total_seconds
    )

    last_clip_name = ""

    while current_time < end_time:

        remaining_seconds = int(
            (end_time - current_time).total_seconds()
        )

        if remaining_seconds <= SHORTEST_AD_DURATION:

            best_file, best_duration = find_best_clip(
                ads_files,
                remaining_seconds,
                30,
                last_clip_name
            )

        else:

            best_file, best_duration = find_best_clip(
                ads_files,
                remaining_seconds,
                MAX_DELAY,
                last_clip_name
            )

        if not best_file:
            break

        clip_name = os.path.splitext(
            os.path.basename(best_file)
        )[0]

        playlist_items.append(

            create_item(
                template_item,
                index,
                clip_name,
                best_file,
                current_time,
                best_duration,
                ""
            )

        )

        index += 1

        current_time += timedelta(
            seconds=best_duration
        )

        last_clip_name = os.path.basename(
            best_file
        )

    # ====================================
    # Jump To
    # ====================================

    playlist_items.append({

    "TrimmerSettings": {
        "ScaleType": "",
        "Interlace": "",
        "AspectRatio": "",
        "Deinterlace": False,
        "CropL": 0,
        "CropR": 0,
        "CropT": 0,
        "CropB": 0,
        "AudioInformations": "0~0|0~0|0~0|0~0|0~0|0~0|0~0|0~0|"
    },

    "OriginalDuration": "0",

    "AutoStartDate": "",

    "AutoStartTime": "",

    "FullStartTime": current_time.strftime(
        '%Y-%m-%dT%H:%M:%S'
    ),

    "index": index,

    "ItemType": 24,

    "ItemObject": {
        "JumpTarget": 0
    },

    "IsLoop": False,

    "BlockName": "",

    "uniquePINumber": str(
        uuid.uuid4()
    ),

    "Thumbnail": "",

    "No": None,

    "Name": "JUMPTO - 1",

    "StartTime": current_time.strftime(
        "%H:%M:%S"
    ),

    "Duration": "00:00:00:00",

    "In": "00:00:00:00",

    "Out": "00:00:00:00",

    "DoubleIn": 0.0,

    "DoubleOut": 0.0,

    "DoubleDuration": 0.0,

    "Category": "Event : JUMPTO",

    "Notes": "1",

    "HouseID": "",

    "Metadata1": "",

    "Metadata2": "",

    "Metadata3": "",

    "Path": ""
})

    # ====================================
    # حساب مدة اللستة الحقيقية
    # ====================================

    playlist_duration_seconds = int(

        (
            current_time -

            datetime.strptime(
                playlist_start_time + ":00",
                "%H:%M:%S"
            )

        ).total_seconds()

    )

    hours = playlist_duration_seconds // 3600

    minutes = (
        playlist_duration_seconds % 3600
    ) // 60

    seconds = playlist_duration_seconds % 60

    playlist_duration = (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )

   

    # ====================================
    # تحديث بيانات اللستة
    # ====================================

    schedule["playlistName"] = folder_name

    current_year = datetime.now().strftime(
        "%Y"
    )

    month_numbers = re.findall(
        r'\d+',
        month_name
    )

    month_number = month_numbers[0].zfill(2)

    day_numbers = re.findall(
        r'\d+',
        folder_name
    )

    day_number = day_numbers[0].zfill(2)

    playlist_date = (
        f"{current_year}/"
        f"{month_number}/"
        f"{day_number}"
    )

    schedule["startDate"] = playlist_date

    schedule["endDate"] = playlist_date
    

    schedule["PlaylistItems"] = playlist_items

    schedule["Duration"] = playlist_duration

    schedule["duration"] = playlist_duration

    schedule["startTime"] = (
        playlist_start_time + ":00"
    )

    schedule["endTime"] = current_time.strftime(
        "%H:%M:%S"
    )

    total_seconds = int(
        (
            current_time -
            datetime.strptime(
                playlist_start_time + ":00",
                "%H:%M:%S"
            )
        ).total_seconds()
    )

    schedule["dblDur"] = float(
        total_seconds
    )

    # ====================================
    # Marsis Playlist Structure
    # ====================================

    OUTPUT_ROOT = r"C:\Marsis_Playlist"

    # ====================================
    # قراءة كود القناة
    # ====================================

    channel_code_file = os.path.join(
        BASE,
        "Settings",
        "channel_code.txt"
    )

    if os.path.exists(channel_code_file):

        with open(
            channel_code_file,
            "r",
            encoding="utf-8"
        ) as f:

            channel_name = f.read().strip()

    else:

        channel_name = "CH1"

    current_year = datetime.now().strftime(
        "%Y"
    )

    # استخراج رقم الشهر

    month_numbers = re.findall(
        r'\d+',
        month_name
    )

    if month_numbers:

        month_number = month_numbers[0].zfill(2)

    else:

        month_number = "01"

    # استخراج رقم اليوم

    day_numbers = re.findall(
        r'\d+',
        folder_name
    )

    if day_numbers:

        day_number = day_numbers[0].zfill(2)

    else:

        day_number = "01"

    # ====================================
    # إنشاء الهيكلية
    # ====================================

    day_folder = os.path.join(
        OUTPUT_ROOT,
        channel_name,
        current_year,
        month_number,
        day_number
    )

    os.makedirs(
        day_folder,
        exist_ok=True
    )

    # ====================================
    # حفظ ملف الجدولة
    # ====================================

    output_file = os.path.join(
        day_folder,
        folder_name + ".MP"
    )

    print(output_file)

    with open(
        output_file,
        'w',
        encoding='utf-8'
    ) as f:

        f.write(

            json.dumps(
                schedule,
                ensure_ascii=False
            )

        )

    print(f"DONE: {output_file}")




