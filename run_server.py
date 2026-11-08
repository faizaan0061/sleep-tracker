import os
import sys

os.chdir("/Users/faizaan/Documents/Projects/recovery-tracker")
sys.path.insert(0, "/Users/faizaan/Documents/Projects/recovery-tracker")

import uvicorn
uvicorn.run("main:app", host="127.0.0.1", port=8000)
