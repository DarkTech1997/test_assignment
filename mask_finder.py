#!/usr/bin/env python3
"""
mask_finder.py – поиск минимальной маски между двумя IP-адресами.
Использование: python mask_finder.py <IP1> <IP2>
Версия python: 3.10
"""
import sys

def detect_version(ip: str) -> int:
    """
    Определяет версию IP-адреса по простым эвристикам.
    Возвращает:
        4 – если похоже на IPv4 (есть точка и нет двоеточия)
        6 – если похоже на IPv6 (есть двоеточие)
        0 – если не похоже ни на то, ни на другое
    Полная валидация формата выполняется позже в функции ip_to_int.
    """
    if '.' in ip and not ':' in ip:
        return 4
    if ':' in ip:
        return 6
    return 0

def ip_to_int(ip: str, v1: int) -> int:
    """
    Преобразует IP-адрес (строку) в целое число.
    Параметры:
        ip – адрес в виде строки
        v1 – версия (4 или 6), определённая ранее
    Возвращает:
        32-битное целое для IPv4, 128-битное для IPv6.
    Выбрасывает ValueError при неверном формате.
    """
    # ----- Блок для IPv4 -----
    if v1 == 4:
        parts = ip.split('.')
        if len(parts) != 4:
            raise ValueError(f"Invalid IPv4: {ip}")

        result = 0
        for p in parts:
            num = int(p)
            if num < 0 or num > 255:
                raise ValueError(f"Octet out of range 0-255: {p}")
            result = (result << 8) | num
        return result

    # ----- Блок для IPv6 -----
    else:
        # Обрабатываем сжатие '::' (два двоеточия подряд)
        if '::' in ip:
            left, right = ip.split('::', 1)
            left_groups = left.split(':') if left else []
            right_groups = right.split(':') if right else []
            # Вычисляем, сколько групп заменяет '::'
            missing = 8 - (len(left_groups) + len(right_groups))
            if missing < 0:
                raise ValueError(f"Too many groups in IPv6: {ip}")
            # Собираем полный список из 8 групп (недостающие заполняем '0')
            groups = left_groups + ['0'] * missing + right_groups
        else:
            # Если '::' нет, разбиваем по ':' и проверяем количество групп
            groups = ip.split(':')
            if len(groups) != 8:
                raise ValueError(f"IPv6 must contain 8 groups: {ip}")
        result = 0
        for g in groups:
            # Каждая группа должна содержать от 1 до 4 шестнадцатеричных цифр
            if len(g) > 4 or len(g) == 0:
                raise ValueError(f"Invalid IPv6 group: {g}")
            try:
                # Преобразуем шестнадцатеричную строку в число (16 бит)
                val = int(g, 16)
            except ValueError:
                raise ValueError(f"Not a hexadecimal number in IPv6: {g}")
            result = (result << 16) | val
        return result


def main():
    # Проверяем, что передано ровно 2 аргумента (IP1 и IP2)
    if len(sys.argv) != 3:
        prog = sys.argv[0]
        print(f"Usage: {prog} <IP1> <IP2>")
        print(f"Example: {prog} 192.168.1.1 192.168.2.1")
        print(f"        {prog} 2001:db8::1 2001:db8::2")
        sys.exit(1)
    ip1, ip2 = sys.argv[1], sys.argv[2]
    try:
        v1 = detect_version(ip1)
        v2 = detect_version(ip2)
        if v1 == 0 or v2 == 0:
            raise ValueError("One of the addresses has invalid format")
        if v1 != v2:
            raise ValueError("IP addresses of different versions (IPv4 and IPv6)")
        total_bits = 32 if v1 == 4 else 128
        num1 = ip_to_int(ip1, v1)
        num2 = ip_to_int(ip2, v1)
        # Вычисляем длину общего префикса (минимальную маску)
        if num1 != num2:
            diff = num1 ^ num2
            mask_len = total_bits - diff.bit_length()
        else:
            mask_len = total_bits
        print(f"/{mask_len}")
        sys.exit(0)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()