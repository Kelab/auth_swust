import os
from dotenv import load_dotenv

load_dotenv(verbose=True)
os.environ["no_proxy"] = "*"
