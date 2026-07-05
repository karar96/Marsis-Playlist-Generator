import os
import sys

# ====================================
# Application Directory
# ====================================

if getattr(sys, "frozen", False):

    APP_DIR = os.path.dirname(
        sys.executable
    )

else:

    APP_DIR = os.path.dirname(
        os.path.dirname(__file__)
    )

# ====================================
# Configs
# ====================================

CONFIGS_DIR = os.path.join(
    APP_DIR,
    "configs"
)

# ====================================
# Channels
# ====================================

CHANNELS_ROOT = r"C:\Users\marsis\Desktop\Channels"