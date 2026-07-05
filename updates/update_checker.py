import requests

# ====================================
# GitHub Repository
# ====================================

GITHUB_REPO = "karar96/Marsis-Playlist-Generator"




# ====================================
# Check For Updates
# ====================================

def check_for_updates(current_version):

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/releases/latest"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )



        if response.status_code != 200:

            return (
                False,
                "Unable to check for updates."
            )

        data = response.json()

        latest_version = data["tag_name"]

        latest_version_name = data["name"]

        release_notes = data.get(
            "body",
            ""
        )


        # ====================================
        # Published Date
        # ====================================

        published_date = data.get(
            "published_at",
            ""
        )

        if published_date:

            published_date = published_date[:10]

        download_url = data.get(
            "html_url",
            ""
        )

        assets = data.get(
            "assets",
            []
        )

        download_size = ""

        if assets:

            size_bytes = assets[0].get(
                "size",
                0
            )

            download_size = (
                f"{size_bytes / (1024 * 1024):.1f} MB"
            )

            direct_download = assets[0].get(
                "browser_download_url",
                download_url
            )

        else:

            direct_download = download_url

        if latest_version == current_version:

            return (
                True,
                latest_version,
                latest_version_name,
                release_notes,
                direct_download,
                published_date,
                download_size
            )

        return (
            False,
            latest_version,
            latest_version_name,
            release_notes,
            direct_download,
            published_date,
            download_size
        )

    except Exception as e:

        print(e)

        return (
            False,
            str(e)
        )

if __name__ == "__main__":

    print(
        check_for_updates("v1.2")
    )