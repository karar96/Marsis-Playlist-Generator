import os
import sys
import platform
import webbrowser

import customtkinter as ctk

from config.version import (
    APP_NAME,
    APP_VERSION_NAME,
    APP_DEVELOPER,
    APP_COPYRIGHT,
    APP_GITHUB
)


class AboutDialog(ctk.CTkToplevel):

    def __init__(
    self,
    parent,
    check_updates_callback=None
    ):

        super().__init__(parent)

        self.check_updates_callback = check_updates_callback

        self.title(APP_NAME)

        self.geometry("760x620")

        self.resizable(False, False)

        self.grab_set()

        self.setup_icon()

        self.build_header()

        self.build_information()

        self.build_buttons()

    def setup_icon(self):

        if getattr(sys, "frozen", False):

            icon_path = os.path.join(
                os.path.dirname(sys.executable),
                "icon.ico"
            )

        else:

            icon_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "icon.ico"
            )

        icon_path = os.path.abspath(icon_path)

        if os.path.exists(icon_path):

            self.iconbitmap(icon_path)


    def build_header(self):

        ctk.CTkLabel(

            self,

            text=APP_NAME,

            font=("Segoe UI", 26, "bold")

        ).pack(
            pady=(25, 5)
        )

        ctk.CTkLabel(

            self,

            text=APP_VERSION_NAME,

            font=("Segoe UI", 18)

        ).pack()

        ctk.CTkLabel(

            self,

            text=f"Developed by {APP_DEVELOPER}",

            font=("Segoe UI", 15)

        ).pack(
            pady=(10,20)
        )


    def build_information(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        self.add_info_row(
            frame,
            "Developer",
            APP_DEVELOPER
        )

        self.add_info_row(
            frame,
            "Version",
            APP_VERSION_NAME
        )

        self.add_info_row(
            frame,
            "Python",
            platform.python_version()
        )

        self.add_info_row(
            frame,
            "Platform",
            platform.platform()
        )

        self.add_info_row(
            frame,
            "Copyright",
            APP_COPYRIGHT
        )


    def add_info_row(
        self,
        parent,
        title,
        value
    ):

        row = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=15,
            pady=6
        )

        ctk.CTkLabel(

            row,

            text=title,

            width=120,

            anchor="w",

            font=("Segoe UI", 14, "bold")

        ).pack(
            side="left"
        )

        ctk.CTkLabel(

            row,

            text=value,

            anchor="w",

            justify="left"

        ).pack(
            side="left",
            padx=15
        )


    def build_buttons(self):

        # ====================================
        # Main Buttons
        # ====================================

        buttons_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        buttons_frame.pack(
            pady=(25, 10)
        )

        self.github_button = ctk.CTkButton(

            buttons_frame,

            text="🌐 Repository",

            width=170,

            command=self.open_github

        )

        self.github_button.pack(
            side="left",
            padx=10
        )

        self.copy_button = ctk.CTkButton(

            buttons_frame,

            text="📋 Copy Info",

            width=170,

            command=self.copy_info

        )

        self.copy_button.pack(
            side="left",
            padx=10
        )

        self.update_button = ctk.CTkButton(

            buttons_frame,

            text="🔄 Updates",

            width=170,

            command=self.check_updates

        )

        self.update_button.pack(
            side="left",
            padx=10
        )

        # ====================================
        # Close Button
        # ====================================

        close_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        close_frame.pack(
            pady=(0, 20)
        )

        self.close_button = ctk.CTkButton(

            close_frame,

            text="Close",

            width=180,

            command=self.destroy

        )

        self.close_button.pack()

    def open_github(self):

        webbrowser.open(
            APP_GITHUB
        )

    def copy_info(self):

        info = (

            f"{APP_NAME}\n\n"

            f"Version : {APP_VERSION_NAME}\n"

            f"Developer : {APP_DEVELOPER}\n"

            f"Python : {platform.python_version()}\n"

            f"Platform : {platform.platform()}\n\n"

            f"{APP_GITHUB}"

        )

        self.clipboard_clear()

        self.clipboard_append(
            info
        )

    # ====================================
    # Check Updates
    # ====================================

    def check_updates(self):

        if self.check_updates_callback:

            self.destroy()

            self.check_updates_callback()