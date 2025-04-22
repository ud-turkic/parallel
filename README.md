# parallel

## Installing all the submodules with a virtual environment

```bash
# Create a virtual environment
python3 -m venv venv
# Activate the virtual environment
source venv/bin/activate
# Install the required packages
pip install -r requirements.txt
# Install the submodules
git submodule update --init --recursive
```
