import os
import tkinter as tk
import webbrowser
import re
import sys
import json
import threading
import subprocess
import customtkinter as ctk
import xml.etree.ElementTree as ET
from datetime import datetime
from generate import generate_playlists
from updates.update_checker import check_for_updates
from dialogs.update_dialog import UpdateDialog
from dialogs.about_dialog import AboutDialog




from moviepy import VideoFileClip

from tkinter import (
    filedialog,
    messagebox,
    StringVar
)

from config.version import (
    APP_NAME,
    APP_VERSION,
    APP_VERSION_NAME,
    APP_DEVELOPER
)

from config.constants import (
    APP_DIR,
    CONFIGS_DIR,
    CHANNELS_ROOT
)

# ====================================
# Smart Series Scanner
# ====================================

def scan_daily_series():

    base = selected_base.get().strip()

    month = selected_month.get().strip()

    content_folder = os.path.join(
        base,
        "Content",
        month
    )

    if not os.path.exists(content_folder):
        return {}

    result = {}

    folders = sorted([

        f for f in os.listdir(content_folder)

        if os.path.isdir(
            os.path.join(content_folder, f)
        )

    ])

    for folder in folders:

        folder_path = os.path.join(
            content_folder,
            folder
        )

        detected_series = set()

        files = os.listdir(folder_path)

        for file in files:

            if file.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            )):

                clean_name = clean_series_name(
                    file
                )

                detected_series.add(
                    clean_name
                )

        result[folder] = sorted(
            list(detected_series)
        )

    return result

# ====================================
# تنظيف اسم المسلسل
# ====================================

def clean_series_name(name):

    name = os.path.splitext(name)[0]

    # حذف ح15
    name = re.sub(
        r'\s*[حhH]\s*\d+.*$',
        '',
        name
    )

    # حذف E15
    name = re.sub(
        r'\s*[eE]\d+.*$',
        '',
        name
    )

    # حذف Episode 15
    name = re.sub(
        r'\s*Episode\s*\d+.*$',
        '',
        name,
        flags=re.IGNORECASE
    )

    # حذف ep15
    name = re.sub(
        r'\s*ep\s*\d+.*$',
        '',
        name,
        flags=re.IGNORECASE
    )

    return name.strip()


# ====================================
# Normalize Series Name
# ====================================

def normalize_series_name(name):

    name = re.sub(
        r'ح\d+',
        '',
        name
    )

    return name.strip()
# ====================================
# Detect Series Changes
# ====================================

def detect_series_changes():

   
    daily_data = scan_daily_series()

    folders = sorted(

        daily_data.keys(),

        key=lambda x: int(
            x.split("-")[0]
        )

       )
    changes = []

    for i in range(1, len(folders)):

        previous_day = folders[i - 1]

        current_day = folders[i]

        previous_series = set(

            normalize_series_name(s)

            for s in daily_data[
                previous_day
            ]
        )

        current_series = set(

            normalize_series_name(s)

            for s in daily_data[
                current_day
            ]
        )

        missing = previous_series - current_series

        new = current_series - previous_series

        if missing or new:

            changes.append({

                "day": current_day,

                "missing": sorted(
                    list(missing)
                ),

                "new": sorted(
                    list(new)
                )

            })

    print(daily_data)

    print(changes)

    return changes

# ====================================
# Smart Replacement Suggestions
# ====================================

def get_replacement_map():

    changes = detect_series_changes()

  

    replacements = {}

    for change in changes:

        

        day = change["day"]

        missing = change["missing"]

        new = change["new"]

        replacements[day] = {}

        for old, new_item in zip(
            missing,
            new
        ):

           

            replacements[day][old] = new_item

    

    return replacements


# ====================================
# تحديث التنبيهات
# ====================================

def update_alerts():

    changes = detect_series_changes()

    alerts_box.configure(
        state="normal"
    )

    alerts_box.delete(
        "1.0",
        "end"
    )

    if not changes:

        alerts_box.insert(
            "end",
            "No Series Changes Detected ✅"
        )

    else:

        alerts_box.insert(
            "end",
           f"Total Alerts: {len(changes)}\n\n"
        )

        alerts_box.insert(
            "end",
            "──────────────────\n\n"
        )

        for change in changes:

            alerts_box.insert(
                "end",
                f"📅 {change['day']}\n\n"
            )

            if change["missing"]:

                alerts_box.insert(
                    "end",
                    "Removed:\n"
                )

                for item in change["missing"]:

                    alerts_box.insert(
                        "end",
                        f"  - {item}\n"
                    )

            if change["new"]:

                alerts_box.insert(
                    "end",
                    "\nAdded:\n"
                )

                for item in change["new"]:

                    alerts_box.insert(
                        "end",
                        f"  + {item}\n"
                    )

            alerts_box.insert(
                "end",
                "\n──────────────────\n\n"
            )

    alerts_box.configure(
        state="disabled"
    )


# ====================================
# إعدادات الواجهة
# ====================================

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("blue")

# ====================================
# النافذة الرئيسية
# ====================================

app = ctk.CTk()

app.title(APP_NAME)

app.state("zoomed")

app.resizable(True, True)


# ====================================
# Check For Updates
# ====================================

def menu_check_updates():

    result = check_for_updates(APP_VERSION)

    # إذا صار خطأ بالاتصال أو بالـ API
    if len(result) < 5:

        error_message = (
            result[1]
            if len(result) > 1
            else "Unable to check for updates."
        )

        messagebox.showerror(
            "Update",
            error_message
        )

        return

    (
        is_latest,
        latest_tag,
        latest_name,
        release_notes,
        download_url,
        published_date,
        download_size
    ) = result

    if is_latest:

        messagebox.showinfo(
            "Updates",
            f"You are using the latest version.\n\n"
            f"{latest_name}"
        )

        return

    UpdateDialog(
        app,
        APP_VERSION_NAME,
        latest_name,
        release_notes,
        download_url,
        published_date,
        download_size
    )

# ====================================
# About
# ====================================

def menu_about():

    AboutDialog(

        app,

        check_updates_callback=menu_check_updates

    )

# ====================================
# Menu Bar
# ====================================

menu_bar = tk.Menu(app)

app.config(menu=menu_bar)

file_menu = tk.Menu(
    menu_bar,
    tearoff=0
)

tools_menu = tk.Menu(
    menu_bar,
    tearoff=0
)

help_menu = tk.Menu(
    menu_bar,
    tearoff=0
)

menu_bar.add_cascade(
    label="File",
    menu=file_menu
)

menu_bar.add_cascade(
    label="Tools",
    menu=tools_menu
)

menu_bar.add_cascade(
    label="Help",
    menu=help_menu
)

# ====================================
# Help Menu
# ====================================

help_menu.add_command(
    label="Check for Updates...",
    command=menu_check_updates
)

help_menu.add_command(
    label="About",
    command=menu_about
)

help_menu.add_separator()

help_menu.add_command(
    label="GitHub Repository",
    command=lambda: webbrowser.open(
        "https://github.com/karar96/Marsis-Playlist-Generator"
    )
)

help_menu.add_separator()


# ====================================
# المتغيرات
# ====================================

selected_base = ctk.StringVar()

selected_channel = ctk.StringVar()

selected_month = ctk.StringVar()

playlist_start_time = ctk.StringVar(
    value="16:00"
)

# ====================================
# Generate Modes
# ====================================

generate_mode = ctk.StringVar(value="all")

selected_day = ctk.StringVar()

from_day = ctk.StringVar()

to_day = ctk.StringVar()

available_series = []

series_entries = []

slot_type_entries = []

hour_labels = []

duration_cache = {}

CHANNELS_ROOT = r"C:\Users\marsis\Desktop\Channels"

# ====================================
# تحديد مسار التطبيق
# ====================================

if getattr(sys, 'frozen', False):

    APP_DIR = os.path.dirname(
        sys.executable
    )

else:

    APP_DIR = os.path.dirname(
        __file__
    )

CONFIGS_DIR = os.path.join(
    APP_DIR,
    "configs"
)

# ====================================
# اسم القناة الحالي
# ====================================

def get_channel_name():

    base = selected_base.get().strip()

    if not base:
        return "default"

    return os.path.basename(base)

# ====================================
# تحميل الأشهر
# ====================================

def load_months(base_path):

    content_folder = os.path.join(
        base_path,
        "Content"
    )

    if not os.path.exists(content_folder):
        return []

    months = [

        f for f in os.listdir(content_folder)

        if os.path.isdir(
            os.path.join(content_folder, f)
        )

    ]

    return sorted(months)

# ====================================
# تحميل القنوات
# ====================================

def load_channels():

    if not os.path.exists(CHANNELS_ROOT):
        return []

    return sorted([

        f for f in os.listdir(CHANNELS_ROOT)

        if os.path.isdir(
            os.path.join(CHANNELS_ROOT, f)
        )

    ])



# ====================================
# تحميل الأيام
# ====================================

def load_days(base_path):

    month = selected_month.get().strip()

    content_folder = os.path.join(
        base_path,
        "Content",
        month
    )

    if not os.path.exists(content_folder):
        return []

    days = [

        f for f in os.listdir(content_folder)

        if os.path.isdir(
            os.path.join(content_folder, f)
        )

    ]

    return sorted(

        days,

        key=lambda x: int(
            x.split("-")[0]
        )

    )

# ====================================
# تحديث الأيام
# ====================================

def refresh_days():

    days = load_days(
        selected_base.get()
    )

    single_day_menu.configure(
        values=days
    )

    from_day_menu.configure(
        values=days
    )

    to_day_menu.configure(
        values=days
    )

    if days:

        selected_day.set(days[0])

        from_day.set(days[0])

        to_day.set(days[-1])

# ====================================
# تغيير القناة
# ====================================

def on_channel_change(choice):

    channel_path = os.path.join(
        CHANNELS_ROOT,
        choice
    )

    selected_base.set(channel_path)

    # ====================================
    # تحميل الأشهر
    # ====================================

    months = load_months(channel_path)

    month_selector.configure(
        values=months
    )

    if months:

        selected_month.set(months[0])

        month_selector.set(months[0])

    refresh_days()

    refresh_series_list(channel_path)

    update_dropdowns()

    update_alerts()

    update_health_report()

    load_config()

# ====================================
# تحديث أسماء المسلسلات
# ====================================

def refresh_series_list(base_path):

    global available_series

    month = selected_month.get().strip()

    content_folder = os.path.join(
        base_path,
        "Content",
        month
    )

    if not os.path.exists(content_folder):
        return

    folders = [

        f for f in os.listdir(content_folder)

        if os.path.isdir(
            os.path.join(content_folder, f)
        )

    ]

    all_series = set()

    for folder in folders:

        folder_path = os.path.join(
            content_folder,
            folder
        )

        files = os.listdir(folder_path)

        for file in files:

            if file.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            )):

                

                clean_name = clean_series_name(
                    file
                )

                all_series.add(
                       clean_name

                )

    available_series = sorted(
        list(all_series)
    )

    update_dropdowns()

# ====================================
# تحديث القوائم
# ====================================

def update_dropdowns():

    for combo in series_entries:

        current_value = combo.get()

        combo.configure(
            values=available_series
        )

        if (
            current_value
            and
            current_value in available_series
        ):

            combo.set(
                current_value
            )

        elif available_series:

            combo.set(
                available_series[0]
            )

    start_preview_update()

    update_health_report()

# ====================================
# حفظ الإعدادات
# ====================================

def save_config():

    os.makedirs(
        CONFIGS_DIR,
        exist_ok=True
    )

    config_file = os.path.join(
        CONFIGS_DIR,
        f"{get_channel_name()}.json"
    )

    data = {

        "base_path": selected_base.get(),

        "month": selected_month.get(),

        "series": [

            combo.get()

            for combo in series_entries
        ]
    }

    with open(
        config_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# ====================================
# تحميل الإعدادات
# ====================================

def load_config():

    config_file = os.path.join(
        CONFIGS_DIR,
        f"{get_channel_name()}.json"
    )

    if not os.path.exists(config_file):
        return

    try:

        with open(
            config_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        saved_base = data.get(
            "base_path",
            ""
        )

        if saved_base and os.path.exists(saved_base):

            selected_base.set(saved_base)

            refresh_series_list(saved_base)



        saved_month = data.get(
            "month",
            ""
        )

        if saved_month:

            selected_month.set(saved_month)

            month_selector.set(saved_month)

            refresh_days()

        saved_series = data.get(
            "series",
            []
        )

        for i, value in enumerate(saved_series):

            if i < len(series_entries):

                series_entries[i].set(value)

        refresh_days()

        update_preview()

        update_alerts()

        update_health_report()

        start_preview_update()

    except:
        pass

       

# ====================================
# كاش مدة الفيديو
# ====================================

def get_video_duration(path):

    if path in duration_cache:
        return duration_cache[path]

    try:

        clip = VideoFileClip(path)

        duration = clip.duration

        clip.close()

        duration_cache[path] = duration

        return duration

    except:

        return 0

# ====================================
# تحليل XML النهائي
# ====================================

def analyze_generated_playlists(base):

    schedules_folder = os.path.join(
        base,
        "Schedules"
    )

    result = {

        "tracks": 0,
        "ads": 0,
        "inserts": 0,
        "jumps": 0,
        "duration": 0

    }

    if not os.path.exists(schedules_folder):
        return result

    xml_files = [

        f for f in os.listdir(schedules_folder)

        if f.lower().endswith(".xml")
    ]

    for xml_file in xml_files:

        xml_path = os.path.join(
            schedules_folder,
            xml_file
        )

        try:

            tree = ET.parse(xml_path)

            root = tree.getroot()

            tracks = root.findall(".//track")

            for track in tracks:

                result["tracks"] += 1

                track_type = track.get(
                    "type",
                    ""
                ).lower()

                if "advert" in track_type:

                    result["ads"] += 1

                if "insert" in track_type:

                    result["inserts"] += 1

                if "jump" in track_type:

                    result["jumps"] += 1

                duration = track.get(
                    "duration",
                    "0"
                )

                try:

                    result["duration"] += int(duration)

                except:
                    pass

        except:
            pass

    return result

# ====================================
# تحليل القناة الحقيقي
# ====================================

def analyze_channel():

    base = selected_base.get().strip()

    month = selected_month.get().strip()

    result = {

        "ads_count": 0,
        "inserts_count": 0,
        "total_duration": 0,
        "end_time": "22:00:00",
        "delay_seconds": 0,
        "status": "OK"

    }

    content_folder = os.path.join(
        base,
        "Content",
        month
    )

    total_seconds = 0

    selected_series = [

        combo.get().strip()

        for combo in series_entries

        if combo.get().strip()

    ]

    if os.path.exists(content_folder):

        folders = [

            f for f in os.listdir(content_folder)

            if os.path.isdir(
                os.path.join(content_folder, f)
            )

        ]

        if folders:

            first_folder = os.path.join(
                content_folder,
                folders[0]
            )

            files = os.listdir(first_folder)

            expected_count = len(selected_series)

            

            for series in selected_series:

                for file in files:

                    if series.lower() in file.lower():

                        video_path = os.path.join(
                            first_folder,
                            file
                        )

                        total_seconds += get_video_duration(
                            video_path
                        )

                        break

    # --------------------------------
    # Ads
    # --------------------------------

    ads_folder = os.path.join(
        base,
        "Ads"
    )

    if os.path.exists(ads_folder):

        ads_files = [

            os.path.join(ads_folder, f)

            for f in os.listdir(ads_folder)

            if f.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            ))
        ]

        result["ads_count"] = len(ads_files)

        ads_total = 0

        for ad in ads_files:

            ads_total += get_video_duration(ad)

        total_seconds += ads_total * 3

    else:

        result["status"] = "WARNING"

    # --------------------------------
    # Inserts
    # --------------------------------

    inserts_folder = os.path.join(
        base,
        "Inserts"
    )

    if os.path.exists(inserts_folder):

        insert_files = [

            os.path.join(inserts_folder, f)

            for f in os.listdir(inserts_folder)

            if f.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            ))
        ]

        result["inserts_count"] = len(insert_files)

        inserts_total = 0

        for ins in insert_files:

            inserts_total += get_video_duration(ins)

        total_seconds += inserts_total * 5

    else:

        result["status"] = "WARNING"

    # --------------------------------
    # وقت النهاية
    # --------------------------------

    result["total_duration"] = total_seconds

    start_time = 16 * 3600

    end_time_seconds = start_time + total_seconds

    hours = int(end_time_seconds // 3600)

    minutes = int(
        (end_time_seconds % 3600) // 60
    )

    seconds = int(
        end_time_seconds % 60
    )

    result["end_time"] = (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )

    target_end = 22 * 3600

    delay = int(
        end_time_seconds - target_end
    )

    result["delay_seconds"] = delay

    if abs(delay) > 60:

        result["status"] = "WARNING"

    return result




# ====================================
# Smart Preview Data
# ====================================

def get_preview_status():

    report = validate_schedule_content()

    return report


# ====================================
# تحديث الـ Preview بالخلفية
# ====================================

def start_preview_update():

    threading.Thread(
        target=update_preview,
        daemon=True
    ).start()

# ====================================
# تحديث الـ Preview
# ====================================

def update_preview():

    preview_box.configure(
        state="normal"
    )

    preview_box.delete(
        "1.0",
        "end"
    )

    current_hour = float(
        playlist_start_time.get().split(":")[0]
    )

    preview_start = current_hour

    SLOT_HOURS = {

        "1 Hour": 1,

        "1.5 Hour": 1.5,

        "2 Hours": 2

    }

    for i, combo in enumerate(series_entries):

        series_name = combo.get().strip()

        if not series_name:
            continue

        slot_type = slot_type_entries[i].get()

        duration_hours = SLOT_HOURS.get(
            slot_type,
            1
        )

        start_h = int(current_hour)

        start_m = int(
            (current_hour - start_h) * 60
        )

        end_time = current_hour + duration_hours

        end_h = int(end_time)

        end_m = int(
            (end_time - end_h) * 60
        )

        preview_box.insert(
            "end",
            f"{start_h:02d}:{start_m:02d} → "
            f"{end_h:02d}:{end_m:02d}   "
            f"{series_name}   "
            f"[{slot_type}]\n"
        )

        current_hour = end_time

    total_hours = current_hour - preview_start

    end_h = int(current_hour)

    end_m = int(
        (current_hour - end_h) * 60
    )

    preview_box.insert(
        "end",
        "\n────────────────────\n"
    )

    preview_box.insert(
        "end",
        f"\nTotal Duration ← {total_hours:.1f} Hours"
    )

    preview_box.insert(
        "end",
        f"\nEnd Time ← {end_h:02d}:{end_m:02d}"
    )

    preview_box.insert(
        "end",
        "\n────────────────────\n"
    )




    preview_box.insert(
        "end",
        f"\nMonth ← {selected_month.get()}"
    )

    preview_box.configure(
        state="disabled"
    )

# ====================================
# فحص الأيام والمسلسلات
# ====================================

def validate_schedule_content():

    base = selected_base.get().strip()

    month = selected_month.get().strip()

    content_folder = os.path.join(
        base,
        "Content",
        month
    )

    report = []

    if not os.path.exists(content_folder):

        report.append(
            "❌ Content folder missing"
        )

        return report

    folders = sorted(

        [

            f for f in os.listdir(
                content_folder
            )

            if os.path.isdir(
                os.path.join(
                    content_folder,
                    f
                )
            )

        ],

        key=lambda x: int(
            x.split("-")[0]
        )

    )

    selected_series = [

        combo.get().strip()

        for combo in series_entries

        if combo.get().strip()

    ]

    # ====================================
    # فلترة الأيام حسب Generate Mode
    # ====================================

    mode = generate_mode.get()

    if mode == "single":

        selected = selected_day.get().strip()

        folders = [

            f for f in folders

            if f == selected

        ]

    elif mode == "range":

        start_day = int(
            from_day.get().split("-")[0]
        )

        end_day = int(
            to_day.get().split("-")[0]
        )

        folders = [

            f for f in folders

            if start_day
            <= int(f.split("-")[0])
            <= end_day

        ]




    replacements = get_replacement_map()

    for folder in folders:

        folder_path = os.path.join(
            content_folder,
            folder
        )

        files = os.listdir(folder_path)

        day_report = []

        # ====================================
        # استخراج المسلسلات الموجودة فعلياً
        # ====================================

        video_series = set()

        for file in files:

            if file.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            )):

                clean_name = clean_series_name(
                    file
                )

                video_series.add(clean_name)

        expected_count = len(selected_series)

        actual_count = len(video_series)

        # ====================================
        # فحص النقص
        # ====================================

        if actual_count < expected_count:

            day_report.append(
                f"Missing Series Count "
                f"({actual_count}/{expected_count})"
            )

        # ====================================
        # عرض التبديلات
        # ====================================

        replacement_found = False

        for replacement_day in replacements:

            if replacement_day == folder:

                for old, new in replacements[
                    replacement_day
                ].items():

                    replacement_found = True

                    report.append(
                        f"⚠ {folder} Replacement Applied"
                    )

                    report.append(
                         f"   {old} → {new}"
                    )

        # ====================================
        # اليوم سليم
        # ====================================

        if not day_report and not replacement_found:

            report.append(
                f"✅ {folder} OK"
            )

        # ====================================
        # Replacement فقط
        # ====================================

        elif replacement_found and not day_report:

            pass

        # ====================================
        # مشاكل فعلية
        # ====================================

        else:

            report.append(
                f"❌ {folder}"
            )

            report.extend(day_report)

    return report

# ====================================
# فحص القناة
# ====================================

def validate_channel():

    base = selected_base.get().strip()

    errors = []

    ads_folder = os.path.join(
        base,
        "Ads"
    )

    if not os.path.exists(ads_folder):

        errors.append(
            "Ads folder missing"
        )

    else:

        ads_files = [

            f for f in os.listdir(ads_folder)

            if f.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            ))
        ]

        if not ads_files:

            errors.append(
                "Ads folder is empty"
            )

    inserts_folder = os.path.join(
        base,
        "Inserts"
    )

    if not os.path.exists(inserts_folder):

        errors.append(
            "Inserts folder missing"
        )

    else:

        insert_files = [

            f for f in os.listdir(inserts_folder)

            if f.lower().endswith((
                ".mp4",
                ".mkv",
                ".mov"
            ))
        ]

        if not insert_files:

            errors.append(
                "Inserts folder is empty"
            )

    category_file = os.path.join(
        base,
        "Settings",
        "category.txt"
    )

    if not os.path.exists(category_file):

        errors.append(
            "category.txt missing"
        )

    month = selected_month.get().strip()

    content_folder = os.path.join(
        base,
        "Content",
        month
    )

    if not os.path.exists(content_folder):

        errors.append(
            "Content folder missing"
        )

    selected_series = [

        combo.get().strip()

        for combo in series_entries

        if combo.get().strip()

    ]

    if not selected_series:

        errors.append(
            "No series selected"
        )

    return errors

# ====================================
# اختيار فولدر القناة
# ====================================

def browse_folder():

    folder = filedialog.askdirectory()

    if folder:

        selected_base.set(folder)

        refresh_series_list(folder)

        load_config()

        refresh_days()

# ====================================
# تحديث تقرير الصحة
# ====================================

def update_health_report():

   

    report = validate_schedule_content()

    total_days = 0

    healthy_days = 0

    replacement_days = 0

    missing_days = 0

    health_box.configure(
        state="normal"
    )

    health_box.delete(
        "1.0",
        "end"
    )

    day_lines = []

    for line in report:

        if (
            line.startswith("✅")
            or line.startswith("⚠")
            or line.startswith("❌")
        ):

            total_days += 1
            day_lines.append(line)

        if line.startswith("✅"):

            healthy_days += 1

        elif line.startswith("⚠"):

            replacement_days += 1

        elif line.startswith("❌"):

            missing_days += 1

    health_box.insert(
        "end",
        "📊 Generated Playlists\n\n"
    )

    health_box.insert(
        "end",
        f"Total Playlists: {total_days}\n\n"
    )

    for day in day_lines:

        health_box.insert(
            "end",
            day + "\n"
        )

    health_box.insert(
        "end",
        "\n────────────────\n\n"
    )

    health_box.insert(
        "end",
        f"🟢 Healthy: {healthy_days}\n"
    )

    health_box.insert(
        "end",
        f"🟡 Replacements: {replacement_days}\n"
    )

    health_box.insert(
        "end",
        f"🔴 Missing: {missing_days}\n"
    )

    if total_days > 0:

        score = int(
            (
                healthy_days
                / total_days
            ) * 100
        )

        health_box.insert(
            "end",
            f"\nHealth Score: {score}%"
        )

    health_box.insert(
        "end",
        "\n\n════════════════\n"
    )

    health_box.insert(
        "end",
        "\n⚙ Current Setup\n\n"
    )

    channel_path = selected_base.get()

    category_file = os.path.join(
        channel_path,
        "Settings",
        "category.txt"
    )

    if os.path.exists(category_file):

        health_box.insert(
            "end",
            "✅ Category Found\n"
        )

    else:

        health_box.insert(
            "end",
            "❌ Missing Category\n"
        )

    code_file = os.path.join(
        channel_path,
        "Settings",
        "channel_code.txt"
    )

    if os.path.exists(code_file):

        health_box.insert(
            "end",
            "✅ Channel Code Found\n"
        )

    else:

        health_box.insert(
            "end",
            "❌ Missing Channel Code\n"
        )

    ads_folder = os.path.join(
        channel_path,
        "Ads"
    )

    ads_count = 0

    if os.path.exists(ads_folder):

        ads_count = len([

            f for f in os.listdir(
                ads_folder
            )

            if os.path.isfile(
                os.path.join(
                    ads_folder,
                    f
                )
            )

        ])

    if ads_count > 0:

        health_box.insert(
            "end",
            f"✅ Ads: {ads_count}\n"
        )

    else:

        health_box.insert(
            "end",
            "❌ No Ads Found\n"
        )

    inserts_folder = os.path.join(
        channel_path,
        "Inserts"
    )

    inserts_count = 0

    if os.path.exists(inserts_folder):

        inserts_count = len([

            f for f in os.listdir(
                inserts_folder
            )

            if os.path.isfile(
                os.path.join(
                    inserts_folder,
                    f
                )
            )

        ])

    if inserts_count > 0:

        health_box.insert(
            "end",
            f"✅ Inserts: {inserts_count}\n"
        )

    else:

        health_box.insert(
            "end",
            "❌ No Inserts Found\n"
        )

    empty_slots = 0

    for combo in series_entries:

        if not combo.get().strip():

            empty_slots += 1

    if empty_slots == 0:

        health_box.insert(
            "end",
            "✅ All Slots Filled\n"
        )

    else:

        health_box.insert(
            "end",
            f"⚠ Empty Slots: {empty_slots}\n"
        )

    total_minutes = 0

    for combo in slot_type_entries:

        total_minutes += get_slot_minutes(
            combo.get()
        )

    duration_hours = round(
        total_minutes / 60,
        1
    )

    end_minutes = (
        16 * 60
        + total_minutes
    )

    end_hour = (
        end_minutes // 60
    ) % 24

    end_minute = (
        end_minutes % 60
    )

    health_box.insert(
        "end",
        f"⏱ Network Duration: {duration_hours} Hours\n"
    )

    health_box.insert(
        "end",
        f"🕒 End Time: {end_hour:02d}:{end_minute:02d}\n"
    )


    health_box.insert(
        "end",
        "\n────────────────\n\n"
    )

    ready = True

    if missing_days > 0:

        ready = False


    if not os.path.exists(category_file):

        ready = False

    if not os.path.exists(code_file):

        ready = False

    if ads_count == 0:

        ready = False

    if inserts_count == 0:

        ready = False

    if empty_slots > 0:

        ready = False

    if ready:

        health_status_label.configure(
            text="READY TO GENERATE",
            text_color="#00C853"
        )

    else:

        health_status_label.configure(
            text="NOT READY TO GENERATE",
            text_color="#FF3D00"
        )

                   

    health_box.configure(
        state="disabled"
    )

# ====================================
# حفظ Logs
# ====================================

def save_log(message):

    logs_folder = os.path.join(
        APP_DIR,
        "logs"
    )

    os.makedirs(
        logs_folder,
        exist_ok=True
    )

    log_file = os.path.join(
        logs_folder,
        "logs.txt"
    )

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"\n[{current_time}]\n"
        )

        f.write(message)

        f.write(
            "\n" + ("─" * 40) + "\n"
        )


# ====================================
# تشغيل Generate
# ====================================

def on_generate_playlists():

    base = selected_base.get().strip()

    month = selected_month.get().strip()

    errors = validate_channel()

    if errors:

        message = "\n".join([

            f"• {e}"

            for e in errors
        ])

        messagebox.showerror(
            "Validation Error",
            message
        )

        return

    if not base:

        messagebox.showerror(
            "Error",
            "اختر قناة أولاً"
        )

        return

    progress.set(0)

    app.update()

    app.configure(cursor="watch")

    app.update()

    content_folder = os.path.join(
        base,
        "Content",
        month
    )

    if not os.path.exists(content_folder):

        messagebox.showerror(
            "Error",
            "Content folder not found"
        )

        app.configure(cursor="")

        return

    # ====================================
    # قراءة الأيام
    # ====================================

    all_folders = [

        f for f in os.listdir(content_folder)

        if os.path.isdir(
            os.path.join(content_folder, f)
        )

    ]

    all_folders = sorted(
        all_folders,
        key=lambda x: int(
             x.split("-")[0]
        )
       )

    mode = generate_mode.get()

    # ====================================
    # All Days
    # ====================================

    if mode == "all":

        folders = all_folders

    # ====================================
    # Single Day
    # ====================================

    elif mode == "single":

        folders = [

            selected_day.get()

        ]

    # ====================================
    # Range
    # ====================================

    elif mode == "range":

        start_day = from_day.get()

        end_day = to_day.get()

        try:

            start_index = all_folders.index(
                start_day
            )

            end_index = all_folders.index(
                end_day
            )

            folders = all_folders[
                start_index:end_index + 1
            ]

        except:

            folders = []

    # ====================================
    # Fallback
    # ====================================

    else:

        folders = all_folders

      # ====================================
    # كتابة schedule.txt
    # ====================================

    

    series_names = []

    for i, combo in enumerate(series_entries):

        value = combo.get().strip()

        if not value:

            continue

        slot_type = slot_type_entries[i].get()

        series_names.append(
            f"{slot_type}|{value}"
        )

    for folder in folders:

        schedule_path = os.path.join(
            content_folder,
            folder,
            "schedule.txt"
        )

        with open(
            schedule_path,
            "w",
            encoding="utf-8"
        ) as f:

            for series in series_names:

                f.write(series + "\n")

    progress.set(0.3)

    app.update()

    # ====================================
    # حفظ Smart Replacements
    # ====================================

    replacement_map = get_replacement_map()

    

    replacement_file = os.path.join(
        APP_DIR,
        "_internal",
        "replacements.json"
    )

    os.makedirs(
        os.path.dirname(replacement_file),
        exist_ok=True
    )

  

    with open(
        replacement_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            replacement_map,
            f,
            ensure_ascii=False,
            indent=4
        )

    status_box.configure(state="normal")

    status_box.delete(
        "1.0",
        "end"
    )

    status_box.insert(
        "end",
        f"Generating {month} playlists...\n"
    )

    status_box.configure(state="disabled")

    try:

        progress.set(0.5)

        app.update()
        print(folders)



        generate_playlists(
            base,
            month,
            folders,
            playlist_start_time.get()
        )

        progress.set(1)

        app.update()

        status_box.configure(state="normal")

        status_box.insert(
            "end",
            "\nDONE SUCCESSFULLY ✅"
        )

        status_box.configure(state="disabled")

        save_config()

        app.configure(cursor="")


        # ====================================
        # إنشاء Log
        # ====================================

        report = validate_schedule_content()

        log_message = (
            f"Channel: {os.path.basename(base)}\n"
            f"Month: {month}\n\n"
        )

        for line in report:

            log_message += line + "\n"

        log_message += (
            "\nGenerate SUCCESS ✅"
        )

        save_log(log_message)



        messagebox.showinfo(
            "Done",
            f"تم إنشاء لستات {month}"
        )

    except Exception as e:

        app.configure(cursor="")

        messagebox.showerror(
            "Error",
            str(e)
        )

# ====================================
# فتح مجلد Schedules
# ====================================

def open_schedules():

    channel_code_file = os.path.join(
        selected_base.get(),
        "Settings",
        "channel_code.txt"
    )

    channel_name = "CH1"

    if os.path.exists(channel_code_file):

        with open(
            channel_code_file,
            "r",
            encoding="utf-8"
        ) as f:

            channel_name = f.read().strip()

    path = os.path.join(
        r"C:\Marsis_Playlist",
        channel_name
    )

    os.startfile(path)

# ====================================
# العنوان
# ====================================

header = ctk.CTkLabel(
    app,
    text=APP_NAME,
    font=("Arial", 30, "bold")
)

header.pack(
    pady=20
)



# ====================================
# Main Layout
# ====================================

main_frame = ctk.CTkFrame(app)

main_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)

# ====================================
# Left Panel
# ====================================

left_panel = ctk.CTkScrollableFrame(
    main_frame,
    width=420
)

left_panel.pack(
    side="left",
    fill="y",
    padx=(0, 10)
)



# ====================================
# Right Panel
# ====================================

right_panel = ctk.CTkFrame(
    main_frame
)

right_panel.pack(
    side="left",
    fill="both",
    expand=True
)


# ====================================
# انشاء قناة جديدة
# ====================================

def create_new_channel():

    win = ctk.CTkToplevel(app)

    win.transient(app)

    win.lift()

    win.focus_force()

    win.title("Create Channel")

    win.geometry("400x360")

    ctk.CTkLabel(
        win,
        text="Channel Name",
        font=("Tahoma", 16)
    ).pack(pady=(15, 5))

    channel_entry = ctk.CTkEntry(
        win,
        width=250,
        font=("Segoe UI", 16)
    )

    channel_entry.pack()

    ctk.CTkLabel(
        win,
        text="Category",
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    category_entry = ctk.CTkEntry(
        win,
        width=250,
        font=("Tahoma", 16)
    )

    category_entry.pack()

    ctk.CTkLabel(
        win,
        text="Channel Code",
        font=("Arial", 18, "bold")
    ).pack(pady=(15, 5))

    code_combo = ctk.CTkOptionMenu(
        win,
        values=["CH1", "CH2"]
    )

    code_combo.pack()

    def create():

        channel_name = (
            channel_entry.get().strip()
        )

        category_name = (
            category_entry.get().strip()
        )

        channel_code = (
            code_combo.get()
        )

        if not channel_name:

            messagebox.showerror(
                "Error",
                "Channel Name required"
            )

            return

        if not category_name:

            category_name = channel_name

        channel_path = os.path.join(
            CHANNELS_ROOT,
            channel_name
        )

        os.makedirs(
            os.path.join(
                channel_path,
                "Ads"
            ),
            exist_ok=True
        )

        os.makedirs(
            os.path.join(
                channel_path,
                "Inserts"
            ),
            exist_ok=True
        )

        os.makedirs(
            os.path.join(
                channel_path,
                "Content"
            ),
            exist_ok=True
        )

        content_path = os.path.join(
            channel_path,
            "Content"
        )

        for month in range(1, 13):

            os.makedirs(
                os.path.join(
                    content_path,
                    f"شهر {month}"
                ),
                exist_ok=True
            )


        os.makedirs(
            os.path.join(
                channel_path,
                "Schedules"
            ),
            exist_ok=True
        )

        settings_path = os.path.join(
            channel_path,
            "Settings"
        )

        os.makedirs(
            settings_path,
            exist_ok=True
        )

        with open(
            os.path.join(
                settings_path,
                "category.txt"
            ),
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                category_name
            )

        with open(
            os.path.join(
                settings_path,
                "channel_code.txt"
            ),
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                channel_code
            )

        channel_selector.configure(
            values=load_channels()
        )

        channel_selector.set(
            channel_name
        )

        win.destroy()

    ctk.CTkButton(
        win,
        text="Create",
        command=create
    ).pack(
        pady=20
    )



# ====================================
# فتح اعدادات القناة
# ====================================

def open_channel_settings():

    channel_name = (
        channel_selector.get().strip()
    )

    if not channel_name:

        return

    channel_path = os.path.join(
        CHANNELS_ROOT,
        channel_name
    )

    settings_path = os.path.join(
        channel_path,
        "Settings"
    )

    category_file = os.path.join(
        settings_path,
        "category.txt"
    )

    code_file = os.path.join(
        settings_path,
        "channel_code.txt"
    )

    category_value = ""

    code_value = "CH1"

    if os.path.exists(category_file):

        with open(
            category_file,
            "r",
            encoding="utf-8"
        ) as f:

            category_value = f.read().strip()

    if os.path.exists(code_file):

        with open(
            code_file,
            "r",
            encoding="utf-8"
        ) as f:

            code_value = f.read().strip()

    win = ctk.CTkToplevel(app)

    win.title(
        f"Settings - {channel_name}"
    )

    win.geometry("500x350")

    win.transient(app)

    win.lift()

    win.focus_force()

    ctk.CTkLabel(
        win,
        text=channel_name,
        font=("Arial", 22, "bold")
    ).pack(
        pady=(15, 10)
    )

    ctk.CTkLabel(
        win,
        text="Category",
        font=("Arial", 18, "bold")
    ).pack(
        pady=(15, 5)
    )

    category_entry = ctk.CTkEntry(
        win,
        width=300,
        font=("Tahoma", 16)
    )



    category_entry.pack()

    category_entry.insert(
        0,
        category_value
    )

    category_entry.focus()


    ctk.CTkLabel(
        win,
        text="Channel Code",
        font=("Arial", 18, "bold")
    ).pack(
        pady=(15, 5)
    )

    code_combo = ctk.CTkOptionMenu(
        win,
        values=["CH1", "CH2"]
    )

    code_combo.pack()

    code_combo.set(
        code_value
    )

    separator = ctk.CTkFrame(
        win,
        height=2
    )

    separator.pack(
        fill="x",
        padx=30,
        pady=15
    )

    def save_settings():

        with open(
            category_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                category_entry.get().strip()
            )

        with open(
            code_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                code_combo.get()
            )

        on_channel_change(
            channel_name
        )

        win.destroy()


    def delete_channel():

        result = messagebox.askyesno(
            "Delete Channel",
            f"Delete channel?\n\n{channel_name}\n\nThis action cannot be undone."
        )

        if not result:

            return

        import shutil

        channels = load_channels()

        if len(channels) <= 1:

            messagebox.showwarning(
                "Warning",
                "Cannot delete the last channel."
            )

            return

        shutil.rmtree(
            channel_path,
            ignore_errors=True
        )

        channels = load_channels()

        channel_selector.configure(
            values=channels
        )

        if channels:

            channel_selector.set(
                channels[0]
            )

            on_channel_change(
                channels[0]
            )

        win.destroy()


    buttons_frame = ctk.CTkFrame(
        win,
        fg_color="transparent"
    )

    buttons_frame.pack(
        pady=20
    )

    ctk.CTkButton(
        buttons_frame,
        text="💾 Save",
        command=save_settings
    ).pack(
        side="left",
        padx=10
    )

    ctk.CTkButton(
        buttons_frame,
        text="📂 Open Folder",
        command=lambda:
            os.startfile(channel_path)
    ).pack(
        side="left",
        padx=10
    )

    ctk.CTkButton(
        win,
        text="🗑 Delete Channel",
        fg_color="#B22222",
        hover_color="#8B0000",
        command=delete_channel
    ).pack(
        pady=(10, 15)
    )



# ====================================
# About Window
# ====================================

def show_about():

    win = ctk.CTkToplevel(app)

    win.title("About")

    win.geometry("450x350")

    win.transient(app)

    win.lift()

    win.focus_force()

    ctk.CTkLabel(
        win,
        text=APP_NAME,
        font=("Arial", 24, "bold")
    ).pack(
        pady=(20, 10)
    )

    ctk.CTkLabel(
        win,
        text=f"Version {APP_VERSION}",
        font=("Arial", 16)
    ).pack(
        pady=5
    )

    ctk.CTkLabel(
        win,
        text=f"Developed by\n{APP_DEVELOPER}",
        font=("Arial", 18)
    ).pack(
        pady=15
    )

    ctk.CTkLabel(
        win,
        text="© 2026",
        font=("Arial", 14)
    ).pack(
        pady=5
    )

    separator = ctk.CTkFrame(
        win,
        height=2
    )

    separator.pack(
        fill="x",
        padx=30,
        pady=15
    )

    ctk.CTkButton(
        win,
        text="Check for Updates",
        state="disabled"
    ).pack(
        pady=10
    )

    ctk.CTkButton(
        win,
        text="OK",
        command=win.destroy
    ).pack(
        pady=10
    )


# ====================================
# اختيار القناة
# ====================================

channels_frame = ctk.CTkFrame(left_panel)

channels_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

channels_label = ctk.CTkLabel(
    channels_frame,
    text="Channel",
    font=("Arial", 20, "bold")
)

channels_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

channel_row = ctk.CTkFrame(
    channels_frame,
    fg_color="transparent"
)

channel_row.pack(
    fill="x",
    padx=10,
    pady=10
)

channel_selector = ctk.CTkOptionMenu(
    channel_row,
    values=load_channels(),
    command=on_channel_change,
    height=40,
    font=("Arial", 16),
    dropdown_font=("Arial", 16)
)

channel_selector.pack(
    side="left",
    fill="x",
    expand=True
)

settings_button = ctk.CTkButton(
    channel_row,
    text="⚙",
    width=45,
    height=40,
    command=open_channel_settings
)

settings_button.pack(
    side="left",
    padx=(5, 0)
)




ctk.CTkButton(
    channels_frame,
    text="+ New Channel",
    command=create_new_channel
).pack(
    fill="x",
    padx=10,
    pady=(0, 10)
)



# ====================================
# اختيار الشهر
# ====================================

month_frame = ctk.CTkFrame(left_panel)

month_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

month_label = ctk.CTkLabel(
    month_frame,
    text="Month",
    font=("Arial", 20, "bold")
)

month_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

month_selector = ctk.CTkOptionMenu(
    month_frame,
    values=[],
    variable=selected_month,
    command=lambda x: (
           refresh_days(),
           refresh_series_list(
               selected_base.get()
          ),
           update_alerts(),
           update_health_report()
      ),
    height=40,
    font=("Arial", 16),
    dropdown_font=("Arial", 16)
)

month_selector.pack(
    fill="x",
    padx=10,
    pady=10
)

# ====================================
# وقت بداية اللستة
# ====================================

start_time_frame = ctk.CTkFrame(left_panel)

start_time_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

start_time_label = ctk.CTkLabel(
    start_time_frame,
    text="Start Time",
    font=("Arial", 20, "bold")
)

start_time_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

time_values = [

    f"{h:02d}:00"

    for h in range(24)

]

start_time_selector = ctk.CTkOptionMenu(
    start_time_frame,
    values=time_values,
    variable=playlist_start_time,
    height=40,
    font=("Arial", 16),
    dropdown_font=("Arial", 16)
)

start_time_selector.pack(
    fill="x",
    padx=10,
    pady=10
)

# ====================================
# اختيار المسار
# ====================================

path_frame = ctk.CTkFrame(left_panel)

path_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

path_entry = ctk.CTkEntry(
    path_frame,
    textvariable=selected_base,
    height=40,
    font=("Arial", 14)
)

path_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=10,
    pady=10
)

browse_btn = ctk.CTkButton(
    path_frame,
    text="Browse",
    width=120,
    height=40,
    command=browse_folder
)

browse_btn.pack(
    side="right",
    padx=10
)






# ====================================
# قائمة المسلسلات
# ====================================

slot_count_var = ctk.StringVar(
    value="6"
)

series_frame = ctk.CTkFrame(left_panel)

series_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

series_label = ctk.CTkLabel(
    series_frame,
    text="Series Order",
    font=("Arial", 22, "bold")
)

series_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

slots_row = ctk.CTkFrame(series_frame)

slots_row.pack(
    fill="x",
    padx=10,
    pady=(0, 10)
)

ctk.CTkLabel(
    slots_row,
    text="Slots",
    width=70
).pack(
    side="left"
)

slots_entry = ctk.CTkEntry(
    slots_row,
    textvariable=slot_count_var,
    width=80
)

slots_entry.pack(
    side="left",
    padx=5
)

slots_container = ctk.CTkFrame(
    series_frame
)

slots_container.pack(
    fill="x",
    padx=5,
    pady=5
)


def get_slot_minutes(slot_type):

    if slot_type == "1 Hour":
        return 60

    if slot_type == "1.5 Hour":
        return 90

    if slot_type == "2 Hours":
        return 120

    return 60


def update_slot_times():

    current_minutes = 16 * 60

    for i, label in enumerate(hour_labels):

        hour = current_minutes // 60

        minute = current_minutes % 60

        label.configure(
            text=f"{hour:02d}:{minute:02d}"
        )

        if i < len(slot_type_entries):

            current_minutes += get_slot_minutes(
                slot_type_entries[i].get()
            )


def on_slot_type_change(value):

    update_slot_times()

    start_preview_update()



def rebuild_slots():

    global series_entries
    global slot_type_entries

    old_values = [

        combo.get()

        for combo in series_entries

    ]

    old_slot_types = [

        combo.get()

        for combo in slot_type_entries

    ]

    series_entries.clear()
    slot_type_entries.clear()
    hour_labels.clear()

    for widget in slots_container.winfo_children():

        widget.destroy()

    slot_count = int(
        slot_count_var.get()
    )

    for i in range(slot_count):

        row = ctk.CTkFrame(
            slots_container
        )

        row.pack(
            fill="x",
            padx=10,
            pady=5
        )

        hour_label = ctk.CTkLabel(
            row,
            text=f"{16 + i}:00",
            width=70,
            font=("Arial", 15, "bold")
        )

        hour_label.pack(
            side="left",
            padx=5
        )

        hour_labels.append(
            hour_label
        )

        type_combo = ctk.CTkOptionMenu(
            row,
            values=[
                "1 Hour",
                "1.5 Hour",
                "2 Hours"
            ],
            width=120
        )

        type_combo.set(
            "1 Hour"
        )

        type_combo.configure(
            command=on_slot_type_change
        )

        type_combo.pack(
            side="left",
            padx=5
        )

        slot_type_entries.append(
            type_combo
        )

        if i < len(old_slot_types):

            try:

                type_combo.set(
                    old_slot_types[i]
                )

            except:

                pass

 

        combo = ctk.CTkOptionMenu(
            row,
            values=[""],
            command=lambda x: start_preview_update(),
            height=38,
            font=("Arial", 16),
            dropdown_font=("Arial", 16)
        )

        combo.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        series_entries.append(combo)

        if i < len(old_values):

            if old_values[i]:

                try:

                    combo.set(
                        old_values[i]
                    )

                except:

                    pass

   
    update_slot_times()


def apply_slots():

    rebuild_slots()

    update_dropdowns()

ctk.CTkButton(
    slots_row,
    text="Apply",
    width=80,
    command=apply_slots
).pack(
    side="left",
    padx=5
)


rebuild_slots()



# ====================================
# Generate Mode
# ====================================

mode_frame = ctk.CTkFrame(left_panel)

mode_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

mode_label = ctk.CTkLabel(
    mode_frame,
    text="Generate Mode",
    font=("Arial", 20, "bold")
)

mode_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

radio_all = ctk.CTkRadioButton(
    mode_frame,
    text="All Days",
    variable=generate_mode,
    value="all",
    command=update_health_report
)

radio_all.pack(
    anchor="w",
    padx=20,
    pady=5
)

radio_single = ctk.CTkRadioButton(
    mode_frame,
    text="Single Day",
    variable=generate_mode,
    value="single",
    command=update_health_report
)

radio_single.pack(
    anchor="w",
    padx=20,
    pady=5
)

single_day_menu = ctk.CTkOptionMenu(
    mode_frame,
    variable=selected_day,
    values=[],
    command=lambda x: update_health_report()
)

single_day_menu.pack(
    fill="x",
    padx=30,
    pady=5
)

radio_range = ctk.CTkRadioButton(
    mode_frame,
    text="Range",
    variable=generate_mode,
    value="range",
    command=update_health_report
)

radio_range.pack(
    anchor="w",
    padx=20,
    pady=5
)

from_day_menu = ctk.CTkOptionMenu(
    mode_frame,
    variable=from_day,
    values=[],
    command=lambda x: update_health_report()
)

from_day_menu.pack(
    fill="x",
    padx=30,
    pady=5
)

to_day_menu = ctk.CTkOptionMenu(
    mode_frame,
    variable=to_day,
    values=[],
    command=lambda x: update_health_report()
)

to_day_menu.pack(
    fill="x",
    padx=30,
    pady=(5, 15)
)

# ====================================
# Preview Timeline
# ====================================

preview_frame = ctk.CTkFrame(right_panel)

preview_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

preview_label = ctk.CTkLabel(
    preview_frame,
    text="Preview Timeline",
    font=("Arial", 22, "bold")
)

preview_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

preview_box = ctk.CTkTextbox(
    preview_frame,
    height=140,
    font=("Tahoma", 16)
)

preview_box.pack(
    fill="x",
    padx=10,
    pady=10
)

preview_box.insert(
    "end",
    "No Preview Yet..."
)

preview_box.configure(
    state="disabled"
)



# ====================================
# Broadcast Alerts
# ====================================

alerts_frame = ctk.CTkFrame(right_panel)

alerts_frame.pack(
    fill="x",
    padx=10,
    pady=(10, 5)
)

alerts_label = ctk.CTkLabel(
    alerts_frame,
    text="Broadcast Alerts",
    font=("Arial", 22, "bold")
)

alerts_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

alerts_box = ctk.CTkTextbox(
    alerts_frame,
    height=180,
    font=("Tahoma", 15)
)

alerts_box.pack(
    fill="x",
    padx=10,
    pady=(0, 10)
)

alerts_box.insert(
    "end",
    "No Alerts Yet..."
)

alerts_box.configure(
    state="disabled"
)

# ====================================
# فتح فولدر اليوم المختار
# ====================================

def open_selected_day_folder():

    month = selected_month.get().strip()

    mode = generate_mode.get()

    if mode == "single":

        folder_path = os.path.join(
            selected_base.get(),
            "Content",
            month,
            selected_day.get().strip()
        )

    elif mode == "range":

        folder_path = os.path.join(
            selected_base.get(),
            "Content",
            month,
            from_day.get().strip()
        )

    else:

        folder_path = os.path.join(
            selected_base.get(),
            "Content",
            month
        )

    if os.path.exists(folder_path):

        os.startfile(folder_path)



# ====================================
# Health Report
# ====================================

health_frame = ctk.CTkFrame(
    right_panel
)

health_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=(5, 10)
)

health_label = ctk.CTkLabel(
    health_frame,
    text="Generated Playlists Summary",
    font=("Arial", 22, "bold")
)

health_label.pack(
    anchor="w",
    padx=10,
    pady=(10, 5)
)

health_box = ctk.CTkTextbox(
    health_frame,
    height=180,
    font=("Tahoma", 15)
)

health_box.pack(
    fill="x",
    padx=10,
    pady=(0, 10)
)

health_box.insert(
    "end",
    "No Report Yet..."
)

health_box.configure(
    state="disabled"
)

health_status_label = ctk.CTkLabel(
    health_frame,
    text="",
    font=("Arial", 18, "bold")
)

health_status_label.pack(
    pady=(5, 10)
)

buttons_frame = ctk.CTkFrame(
    health_frame,
    fg_color="transparent"
)

buttons_frame.pack(
    pady=(0, 10)
)

open_day_button = ctk.CTkButton(
    buttons_frame,
    text="📂 Open Selected Day Folder",
    command=open_selected_day_folder
)

open_day_button.pack(
    side="left",
    padx=5
)

refresh_health_button = ctk.CTkButton(
    buttons_frame,
    text="🔄 Refresh Health Report",
    command=update_health_report
)

refresh_health_button.pack(
    side="left",
    padx=5
)


# ====================================
# الأزرار
# ====================================

buttons_frame = ctk.CTkFrame(left_panel)

buttons_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

generate_btn = ctk.CTkButton(
    buttons_frame,
    text="Generate Playlists",
    height=45,
    font=("Arial", 16, "bold"),
    command=on_generate_playlists
)

generate_btn.pack(
    side="left",
    padx=10,
    pady=15,
    expand=True,
    fill="x"
)

open_btn = ctk.CTkButton(
    buttons_frame,
    text="Open Schedules",
    height=45,
    font=("Arial", 16, "bold"),
    command=open_schedules
)

open_btn.pack(
    side="left",
    padx=10,
    pady=15,
    expand=True,
    fill="x"
)

# ====================================
# Progress Bar
# ====================================

progress = ctk.CTkProgressBar(right_panel)

progress.pack(
    fill="x",
    padx=20,
    pady=(0, 10)
)

progress.set(0)

# ====================================
# صندوق الحالة
# ====================================

status_box = ctk.CTkTextbox(right_panel,
    height=80,
    font=("Consolas", 14)
)

status_box.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

status_box.insert(
    "end",
    "Ready..."
)

status_box.configure(state="disabled")

# ====================================
# تشغيل أول Preview
# ====================================

start_preview_update()

# ====================================
# تشغيل الواجهة
# ====================================

app.mainloop()