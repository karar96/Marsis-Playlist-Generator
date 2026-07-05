import os
import re

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


