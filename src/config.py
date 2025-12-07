import datetime
import os

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "results")
IMAGE_DIR = os.path.join(BASE_DIR, "images")

# Simulation Settings
START_DATE = datetime.date(2004, 1, 1)
END_DATE = datetime.date(2024, 1, 1)
TAX_RATE = 0.20
INITIAL_CASH = 10_000_000.0
TOP_N_STOCKS = 50
WASH_SALE_DAYS = 30
HARVEST_THRESHOLD = -0.05

