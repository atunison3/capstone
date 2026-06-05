# This file is meant as a sandbox environment for understanding the linters and pre-commit
# I'll drop in a few "bugs" or things that will not make it through a quality check
# This will allow us to learn how to branch, make a change, run it through the linter,
# make a correction, commit it, and merge it back into main.

### Ruff Linter
# Some common linter rules are unused imports and line lengths
# Line too long (E501)
# Uncomment new couple of lines, remove the noqa, and either run `ruff check` or try to commit
# import numpy

# my_string = "FLZQGKGRTQBUBVYSEIDGAVFCKMAQLHOBPJBICPSWGHOWUJHVUKGTGFQEAYKELZLZHGKGCCSWBRIVZHRJJGUQNPGLFRJNEUAGVSZKYHVJURWBWWMYGJWHMSVAD"  # noqa: E501
my_string = "FLZQGKGRTQBUBVYSEIDGAVFCKMAQLHOBPJBICPSWGHOWUJHVUKGTGFQEAYKELZLZHGK"
my_string += "GCCSWBRIVZHRJJGUQNPGLFRJNEUAGVSZKYHVJURWBWWMYGJWHMSVAD"


### Bandit
# Bandit is a security linter. Honestly, I don't expect us to break any rules heres.
# If anything, the basic one rule that breaks is a hardcoded password
# Uncomment the next line, save, and either try to commit or run `bandit -r src`
# password = "Super Secret Password"

# A good work around for this is to save the password in your credential manager and use
# python's keyring (pre saved in requirements-dev.txt) to load the password
import keyring  # noqa: E402

system_name = "capstone"
username = "my_username"
password = keyring.get_password(system_name, username)


### mypy
# mypy is a type checker. Most of the time, you won't even notice a rule violation
def return_a_float() -> float:
    return 1.0


# Uncomment the next line and run `mypy src` in terminal
# x: int = return_a_float()  # This will fail because you're assigning x to a float instead of an int


def accepts_an_int(value: int) -> None:
    """
    While type hints like this aren't a syntax fail,
    and won't prevent you from running, it will hinder you when trying to type faster. When you create a function,
    you should add type hinting. This will allow python IDEs to preview what you need to pass in for the arguments.
    While it seems trivial, it can make a huge difference.
    """
    value *= 2


# This type of situation can help you out tremendously since you're passing a str as an int
# This is a great example because it will work! Your fail could be further down the line
# Uncomment this line and run `mypy src` in the terminal
# accepts_an_int('2')
