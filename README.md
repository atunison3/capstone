# capstone

## Installing Repository

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

## Contributing

To contibute, you will need to work on a branch other than main. When you are finished with your changes, push them to your branch and perform a PR. Rules will be enabled such that at least one reviewer must approve changes.

```
git add .  # Or specify which files to add
git commit -m "Commit Message"
git push origin <branch-name>
```

Safety and linting checks will be performed on each push. I suggest running a formatter and linter prior to committing your work.

```
black . # The uncompromising code formatter.
ruff check  # An extremely fast Python linter and code formatter.
bandit . # Python source code security analyzer
mypy .  # Program that will type check your Python code.



### Running Projects

To run a script, simply navigate to the project directory and run `python <script_name>.py`

```
cd capstone
python src/main.py
```
