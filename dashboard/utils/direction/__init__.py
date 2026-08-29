import os
from dotenv import load_dotenv

from .direction_plain import PageDirection as PageDirectionPlain
from .direction_secure import PageDirection as PageDirectionSecure

load_dotenv()


MODE = os.getenv("MODE")

# That needs importing.
if MODE == "production":
    PageDirection = PageDirectionSecure
else:
    PageDirection = PageDirectionPlain