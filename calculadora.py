#!/usr/bin/env python3
"""Calculadora de linha de comando com operações básicas."""

from __future__ import annotations


def calcular(numero1: float, operador: str, numero2: float) -> float:
    """Executa uma operação matemática básica."""
    if operador == "+":
        return numero1 + numero2
    if operador == "-":
        return numero1 - numero2
    if operador == "*":
        return numero1 * numero2
    if operador == "/":
        if numero2 == 0:
            raise ValueError("Divisão por zero não é permitida.")
        return numero1 / numero2

    raise ValueError("Operador inválido. Use +, -, * ou /.")


def ler_numero(mensagem: str) -> float:
    """Lê um número de ponto flutuante do usuário."""
    while True:
        entrada = input(mensagem).strip().replace(",", ".")
        try:
            return float(entrada)
        except ValueError:
            print("Entrada inválida. Digite um número válido.")


def main() -> None:
    """Executa a interface interativa da calculadora."""
    print("=== Calculadora ===")

    while True:
        numero1 = ler_numero("Primeiro número: ")
        operador = input("Operação (+, -, *, /): ").strip()
        numero2 = ler_numero("Segundo número: ")

        try:
            resultado = calcular(numero1, operador, numero2)
            print(f"Resultado: {resultado}")
        except ValueError as erro:
            print(f"Erro: {erro}")

        continuar = input("Deseja fazer outra conta? (s/n): ").strip().lower()
        if continuar != "s":
            print("Até mais!")
            break


if __name__ == "__main__":
    main()
