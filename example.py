# my_functions.py


def greet(name: str) -> None:
    """Greets a user"""

    print(f"Hello {name}")


def multiply_two_numbers(a: int | float, b: int | float) -> int | float:
    """Multiplies two numbers"""

    return a * b
