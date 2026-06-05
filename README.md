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

### Pre-Commits

This project utilizes GitHub actions to perform quality and safety checks. To reduce the burden on shared resources and prevent unnecessary commits dur to fixing these checks, it is **highly recommended** you install the pre-commits.

```
pip install pre-commit
pre-commit install
```

You can further run the quality checks locally by running `pre-commit run --all-files`. Learn more at https://pre-commit.com/. Currently, the pre-commit configuration doesn't check `mypy`. We might want to add that later or remove the `mypy` check in the github if its too much of a problem. Until a solution is found, I recommend manually running `mypy` commands before committing:

```
mypy src
mypy tests
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
```



### Running Projects

To run a script, simply navigate to the project directory and run `python <script_name>.py`

```
python src/main.py
```

### TODOs
