import os
import tempfile
import requests


class UpdateDownloader:

    def __init__(self):

        self.chunk_size = 8192

    # ====================================
    # Installer Path
    # ====================================

    def get_installer_path(
        self,
        filename
    ):

        temp_folder = os.path.join(
            tempfile.gettempdir(),
            "MarsisPlaylistGenerator"
        )

        os.makedirs(
            temp_folder,
            exist_ok=True
        )

        return os.path.join(
            temp_folder,
            filename
        )

    # ====================================
    # Download Update
    # ====================================

    def download(
        self,
        url,
        filename,
        progress_callback=None
    ):

        file_path = self.get_installer_path(
            filename
        )

        response = requests.get(
            url,
            stream=True
        )

        response.raise_for_status()

        total_size = int(
            response.headers.get(
                "content-length",
                0
            )
        )

        downloaded = 0

        with open(
            file_path,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                self.chunk_size
            ):

                if not chunk:
                    continue

                file.write(chunk)

                downloaded += len(chunk)

                if (
                    progress_callback
                    and total_size
                ):

                    progress = (
                        downloaded /
                        total_size
                    )

                    progress_callback(
                        progress
                    )

        return file_path

if __name__ == "__main__":

    downloader = UpdateDownloader()

    url = (
        "https://github.com/karar96/"
        "Marsis-Playlist-Generator/releases/download/"
        "v1.2/Marsis_Playlist_Generator_Setup_v12.exe"
    )

    def progress(value):

        print(
            f"{value * 100:.1f}%"
        )

    file = downloader.download(
        url,
        "Marsis_Playlist_Generator_Setup_v12.exe",
        progress
    )

    print()

    print("Downloaded to:")

    print(file)


