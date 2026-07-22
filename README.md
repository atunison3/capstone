# capstone

## Installing Repository

Verify python version is 3.13. I am using 3.13.2 [Python](https://www.python.org/downloads/release/python-3132/).

```terminal
python --version
python3.13 --version
```

For Windows:

```terminal
python --version
py -3.13 --version
```

Clone the repository. You'll be able to clone it but you'll need permission to push changes.

```terminal
git clone https://github.com/atunison3/capstone.git
```

Install requirements.

```terminal
python -m pip install --upgrade pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m build
```

Windows:

```terminal
python -m pip install --upgrade pip
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m build
```

Set up your jupyter notebook kernel:

```terminal
brew install python@3.13
python3.13 --version
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install notebook ipykernel
python -m ipykernel install --user --name=capstoneDev --display-name="Python 3.13 (Capstone Dev)"
```

### Pre-Commits

This project utilizes GitHub actions to perform quality and safety checks. To reduce the burden on shared resources and prevent unnecessary commits due to fixing these checks, it is **highly recommended** you install the pre-commits.

```terminal
pip install pre-commit
pre-commit install
```

You can further run the quality checks locally by running `pre-commit run --all-files`. Learn more at [pre-commit](https://pre-commit.com/). Currently, the pre-commit configuration doesn't check `mypy`. We might want to add that later or remove the `mypy` check in the github if its too much of a problem. Until a solution is found, I recommend manually running `mypy` commands before committing:

```terminal
mypy src
mypy tests
```

## Contributing

To contibute, you will need to work on a branch other than main. When you are finished with your changes, push them to your branch and perform a PR. Rules will be enabled such that at least one reviewer must approve changes.

```terminal
git add .  # Or specify which files to add
git commit -m "Commit Message"
git push origin <branch-name>
```

Safety and linting checks will be performed on each push. I suggest running a formatter and linter prior to committing your work.

```terminal
black . # The uncompromising code formatter.
ruff check  # An extremely fast Python linter and code formatter.
bandit . # Python source code security analyzer
mypy .  # Program that will type check your Python code.
```

### Running Projects

To run a script, simply navigate to the project directory and run `python <script_name>.py`

```terminal
python src/main.py
```

### TODOs

### Data

You can download the 2024 Cooperative Election Study data and code books from the [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/X11EP6).

* Download a copy of CCES24_Common_OUTPUT_vv_topost_final.csv, and upload it to the capstone/data folder before running the data_cleaning.ipynb file to clean the data.

### Saving data

Save your data on your local machine. Create a `config.local.toml` file in your project root with a parameter `data_path`. Use the function `data_cleaning.load_ces_data` to automatically read in your CES data.

```toml config.local.toml
data_path = "/Users/<username>/Downloads/CES Data"
```
