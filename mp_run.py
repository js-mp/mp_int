#! /usr/bin/python3

import sys
from mp_compiler import *
from mp_interpretator import *


# =====================================================================================================================
def _print_usage():
    print('usage:')
    print('mp_run.py <file_name> <func_name> [<func_params>]')
    print('Binary (0b), hexadecimal (0x) and decimal non-negative numbers are allowed')
    print(f'\ngot: {sys.argv}')


# =====================================================================================================================
# string to number convertion:
#   '0x1a' -> 26
#   '0b1001' -> 9
#   '123' -> 123
def _str_to_int(s):
    if s[0] == '-':
        raise CompilerError(f'negative values are not allowed: {s}')
    match s[:2]:
        case '0x':
            return int(s, 16)
        case '0b':
            return int(s, 2)
        case _:
            return int(s, 10)


# =====================================================================================================================
def _go():
    if len(sys.argv) < 3:
        _print_usage()
        return

    mp_file_name = sys.argv[1]
    func_name = sys.argv[2]
    param = [_str_to_int(v) for v in sys.argv[3:]]
    # print('')
    # for p in sys.argv[1:]:
    #     print(p)
    print('')
    Compiler(mp_file_name, ip_runners()).compile().run(func_name, { 'param': param })


# =====================================================================================================================
if __name__ == '__main__':
    _go()
