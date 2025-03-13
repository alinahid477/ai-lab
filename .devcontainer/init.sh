#!/bin/bash

[ ! -d "myenv" ] && python3 -m venv myenv
source myenv/bin/activate && pip install --no-cache-dir -r /home/dev/requirements.txt

/bin/bash