import os
import sys
import webbrowser
import customtkinter as ctk
import threading
import subprocess

from updates.update_downloader import UpdateDownloader
from tkinter import messagebox
from config.version import APP_NAME


class UpdateDialog(ctk.CTkToplevel):

    def __init__(
        self,
        parent,
        current_version,
        latest_name,
        release_notes,
        download_url,
        published_date,
        download_size
    ):

        super().__init__(parent)

        self.download_url = download_url

        self.current_version = current_version

        self.latest_name = latest_name

        self.release_notes = release_notes

        self.published_date = published_date

        self.download_size = download_size

        self.title(APP_NAME)

        self.geometry("700x700")

        self.resizable(False, False)

        self.grab_set()

        self.setup_icon()

        self.build_header()

        self.build_information()

        self.build_release_notes()

        self.build_buttons()

        downloader = UpdateDownloader()

        filename = self.download_url.split("/")[-1]

        self.installer_path = downloader.get_installer_path(
            filename
        )

        if os.path.exists(self.installer_path):

            self.download_button.configure(
                text="Install Now",
                command=self.install_update
            )

        # ====================================
        # Progress
        # ====================================

        self.progress = ctk.CTkProgressBar(
            self,
            width=500
        )

        self.progress.set(0)

        self.progress.pack(
            pady=(10, 5)
        )

        self.progress.pack_forget()

        self.progress_label = ctk.CTkLabel(

            self,

            text=""

        )

        self.progress_label.pack()

        self.progress_label.pack_forget()

    # ====================================
    # Icon
    # ====================================

    def setup_icon(self):

        if getattr(sys, "frozen", False):

            icon_path = os.path.join(
                os.path.dirname(sys.executable),
                "icon.ico"
            )

        else:

            icon_path = os.path.join(
                os.path.dirname(__file__),
                "icon.ico"
            )

        if os.path.exists(icon_path):

            self.iconbitmap(icon_path)

    # ====================================
    # Header
    # ====================================

    def build_header(self):

        ctk.CTkLabel(

            self,

            text=f"🚀 {APP_NAME} Update",

            font=("Segoe UI", 24, "bold")

        ).pack(pady=(20, 25))

    # ====================================
    # Information
    # ====================================

    def build_information(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            padx=20,
            fill="x"
        )

        frame.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        self.info_box(
            frame,
            0,
            "Current Version",
            self.current_version
        )

        self.info_box(
            frame,
            1,
            "Latest Version",
            self.latest_name
        )

        self.info_box(
            frame,
            2,
            "Published",
            self.published_date
        )

        self.info_box(
            frame,
            3,
            "Download Size",
            self.download_size
        )

    # ====================================
    # Small Info Box
    # ====================================

    def info_box(
        self,
        parent,
        index,
        title,
        value
    ):

        row = index // 2

        column = index % 2

        box = ctk.CTkFrame(parent)

        box.grid(
            row=row,
            column=column,
            padx=8,
            pady=8,
            sticky="ew"
        )

        ctk.CTkLabel(

            box,

            text=title,

            font=("Segoe UI", 13)

        ).pack(
            pady=(8, 2)
        )

        ctk.CTkLabel(

            box,

            text=value,

            font=("Segoe UI", 16, "bold")

        ).pack(
            pady=(0, 8)
        )

    # ====================================
    # Release Notes
    # ====================================

    def build_release_notes(self):

        ctk.CTkLabel(

            self,

            text="Release Notes",

            font=("Segoe UI", 18, "bold")

        ).pack(
            pady=(20, 8)
        )

        self.notes = ctk.CTkTextbox(

            self,

            width=620,

            height=220

        )

        self.notes.pack()

        self.notes.insert(
            "1.0",
            self.release_notes
        )

        self.notes.configure(
            state="disabled"
        )

    # ====================================
    # Buttons
    # ====================================

    def build_buttons(self):

        frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame.pack(
            pady=20
        )

        self.download_button = ctk.CTkButton(
            frame,
            text="Download",
            width=160,
            command=self.start_download
        )

        self.download_button.pack(
            side="left",
            padx=10
        )

        ctk.CTkButton(

            frame,

            text="Later",

            width=160,

            command=self.destroy

        ).pack(
            side="left",
            padx=10
        )

    # ====================================
    # Download
    # ====================================

    def download(self):

        downloader = UpdateDownloader()

        filename = self.download_url.split("/")[-1]

        try:

            file_path = downloader.download(

                self.download_url,

                filename,

                self.update_progress

            )

            self.after(

                0,

                lambda: self.download_finished(file_path)

            )

        except Exception as e:

            self.after(

                0,

                lambda: self.progress_label.configure(

                    text=str(e)

                )

            )

    # ====================================
    # Download Finished
    # ====================================

    def download_finished(
        self,
        file_path
    ):

        self.progress.set(1)

        self.progress_label.configure(

            text="✅ Download Complete"

        )

        self.installer_path = file_path

        self.download_button.configure(
            state="normal",
            text="Install Now",
            command=self.install_update
        )

    # ====================================
    # Start Download
    # ====================================

    def start_download(self):

        self.download_button.configure(
            state="disabled"
        )

        self.progress.pack(
            pady=(10,5)
        )

        self.progress_label.pack()

        threading.Thread(

            target=self.download,

            daemon=True

        ).start()


    # ====================================
    # Update Progress
    # ====================================

    def update_progress(
        self,
        value
    ):

        self.after(

            0,

            lambda: self.progress.set(value)

        )

        self.after(

            0,

            lambda: self.progress_label.configure(

                text=f"Downloading... {value*100:.0f}%"

            )

        )

    # ====================================
    # Install Update
    # ====================================

    def install_update(self):

        answer = messagebox.askyesno(

            "Install Update",

            "The update has been downloaded.\n\n"
            "The application will close before installation.\n\n"
            "Do you want to continue?"

        )

        if not answer:
            return

        subprocess.Popen(
            [self.installer_path]
        )

        self.master.destroy()
