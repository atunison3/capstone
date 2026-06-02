# capstone

## Contributing

Verify python version is 3.13. I am using 3.13.2 https://www.python.org/downloads/release/python-3132/. 

```
python --version
python3.13 --version
```

For Windows:
```
python --version
py -3.13 --version
```

Clone the repository. You'll be able to clone it but you'll need permission to push changes.

```
git clone https://github.com/atunison3/capstone.git
```

Install requirements.

```
cd capstone
python -m pip install --upgrade pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:
```
cd capstone
python -m pip install --upgrade pip
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Running Projects

To run a script, simply navigate to the project directory and run `python <script_name>.py`

```
cd capstone
python src/main.py
```

