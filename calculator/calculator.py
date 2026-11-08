"""Sadə kalkulyator.

İşə salmaq üçün:  python calculator.py
"""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Sıfıra bölmək olmaz!")
    return a / b


OPERATIONS = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide,
}


def read_number(prompt):
    """İstifadəçi düzgün ədəd daxil edənə qədər soruşur."""
    while True:
        text = input(prompt).strip().replace(",", ".")
        try:
            return float(text)
        except ValueError:
            print("Xəta: zəhmət olmasa ədəd daxil edin.")


def read_operation():
    """İstifadəçi düzgün əməliyyat seçənə qədər soruşur."""
    while True:
        op = input("Əməliyyat seçin (+, -, *, /): ").strip()
        if op in OPERATIONS:
            return op
        print("Xəta: yalnız +, -, * və ya / seçə bilərsiniz.")


def format_number(x):
    """5.0 əvəzinə 5 göstərir."""
    return str(int(x)) if x == int(x) else str(round(x, 10))


def main():
    print("=== Sadə Kalkulyator ===")
    while True:
        a = read_number("Birinci ədəd: ")
        op = read_operation()
        b = read_number("İkinci ədəd: ")

        try:
            result = OPERATIONS[op](a, b)
            print(f"Nəticə: {format_number(a)} {op} {format_number(b)} = {format_number(result)}")
        except ZeroDivisionError as e:
            print(f"Xəta: {e}")

        again = input("Davam etmək istəyirsiniz? (b/x): ").strip().lower()
        if again not in ("b", "bəli", "y", "yes"):
            print("Sağ olun!")
            break
        print()


if __name__ == "__main__":
    main()
