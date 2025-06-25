import re


def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(cnpj_parcial, pesos):
        soma = sum(int(a) * b for a, b in zip(cnpj_parcial, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6] + pesos_1

    digito1 = calcular_digito(cnpj[:12], pesos_1)
    digito2 = calcular_digito(cnpj[:12] + digito1, pesos_2)

    if cnpj[-2:] == digito1 + digito2:
        return cnpj
    else:
        return False
