def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Divisão por zero não é permitida.")
    return a / b


def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Entrada inválida. Digite um número.")


def get_operation():
    operations = {
        "1": ("+", add),
        "2": ("-", subtract),
        "3": ("*", multiply),
        "4": ("/", divide),
    }
    print("\nEscolha a operação:")
    print("  1 - Adição (+)")
    print("  2 - Subtração (-)")
    print("  3 - Multiplicação (*)")
    print("  4 - Divisão (/)")
    while True:
        choice = input("Opção: ").strip()
        if choice in operations:
            return operations[choice]
        print("Opção inválida. Escolha 1, 2, 3 ou 4.")


def main():
    print("=== Calculadora Simples ===")
    while True:
        a = get_number("Primeiro número: ")
        symbol, operation = get_operation()
        b = get_number("Segundo número: ")

        try:
            result = operation(a, b)
            print(f"\nResultado: {a} {symbol} {b} = {result}\n")
        except ValueError as e:
            print(f"\nErro: {e}\n")

        again = input("Calcular novamente? (s/n): ").strip().lower()
        if again != "s":
            print("Encerrando. Até mais!")
            break


if __name__ == "__main__":
    main()
