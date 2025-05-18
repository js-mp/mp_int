
from mp_prog_objects import *


# =====================================================================================================================
class IpRunError(Exception):
    def __init__(self, err):
        self.err = err if err != '' else 'ошибка'

    def __str__(self):
        return self.err


# =====================================================================================================================
class IpRunState:
    def __init__(self, stack, f: ProgFunc):
        self.stack = stack.copy()  # нули и единицы
        self._vars_stack = []
        self.vars = {}
        self._f_stack = []
        self.f = f

    def vars_push(self, f: ProgFunc):
        self._vars_stack.append(self.vars)
        self.vars = {}
        self._f_stack.append(self.f)
        self.f = f

    def vars_pop(self):
        self.vars = self._vars_stack.pop()
        self.f = self._f_stack.pop()


# =====================================================================================================================
class IpRunFunc(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgFunc):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        if self.po.native:
            self._run_native(rs, self.po)
        else:
            self._run_code(rs, self.po)

    @staticmethod
    def _run_native(rs: IpRunState, f: ProgFunc):
        if f.descr == 'not:1:1':
            rs.stack.append(rs.stack.pop() ^ 1)
        elif f.descr == 'xor:2:1':
            rs.stack.append(rs.stack.pop() ^ rs.stack.pop())
        elif f.descr == 'or:2:1':
            rs.stack.append(rs.stack.pop() | rs.stack.pop())
        elif f.descr == 'and:2:1':
            rs.stack.append(rs.stack.pop() & rs.stack.pop())
        elif f.descr == 'im:2:1':
            v2 = rs.stack.pop()
            v1 = rs.stack.pop()
            rs.stack.append((v1 ^ 1) | v2)
        else:
            raise IpRunError(f'нет такой native функции: {f.descr}')

    @staticmethod
    def _run_code(rs: IpRunState, f: ProgFunc):
        for name, v in f.vars.items():
            rs.vars[name] = [0] * v.size
        f.block.runner.run(rs)


# =====================================================================================================================
class IpRunVoid(Runner):
    def run(self, rs: IpRunState):
        raise IpRunError('непредвиденная ошибка: неисполняемая инструкция')


# =====================================================================================================================
class IpRunBlock(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgBlock):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        for x in self.po.code:
            x.runner.run(rs)


# =====================================================================================================================
class IpRunIf(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgIf):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        if rs.stack.pop():
            self.po.block.runner.run(rs)
        elif self.po.block_else is not None:
            self.po.block_else.runner.run(rs)


# =====================================================================================================================
class IpRunLoop(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgLoop):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        for _ in range(self.po.nn):
            self.po.block.runner.run(rs)


# =====================================================================================================================
class IpRunReduce(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgReduce):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        n = len(rs.stack) - self.po.nn
        del rs.stack[n:]


# =====================================================================================================================
class IpRunAssign(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgAssign):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        v = self.po
        if v.is_num:
            rs.stack.extend(IpRunProg.bits_int_to_list(v.var, v.nn))
        else:
            if v.var.name not in rs.vars:
                raise IpRunError(f'непредвиденная ошибка: отсутствует переменная {v.var.name} (в {rs.f.descr})')
            vv = rs.vars[v.var.name]
            if v.var_from_stack:
                n = len(rs.stack) - v.nn
                vv.clear()
                vv.extend(rs.stack[n:])
                if not v.var_to_stack:
                    del rs.stack[n:]
            elif v.var_to_stack:
                rs.stack.extend(vv)


# =====================================================================================================================
class IpRunCall(Runner):
    def run(self, rs: IpRunState):
        if not isinstance(self.po, ProgCall):
            raise IpRunError('непредвиденная ошибка: несоответствие типов')
        rs.vars_push(self.po.f)
        self.po.f.runner.run(rs)
        rs.vars_pop()


# =====================================================================================================================
def ip_runners():
    return {
        'Prog': IpRunProg,
        'ProgFunc': IpRunFunc,
        'ProgVar': IpRunVoid,
        'ProgBlock': IpRunBlock,
        'ProgIf': IpRunIf,
        'ProgLoop': IpRunLoop,
        'ProgReduce': IpRunReduce,
        'ProgAssign': IpRunAssign,
        'ProgCall': IpRunCall
    }


# =====================================================================================================================
class IpRunProg:
    def __init__(self, prog: Prog):
        self.prog = prog

    @staticmethod
    def bits_int_to_list(n, p_len):
        """ Преобразование числа в список нулей и единиц """
        bb = bin(n)[2:]
        if len(bb) > p_len:
            raise IpRunError(f'длина фактического параметра {len(bb)} бит больше максимальной {p_len}')
        ret = [0] * p_len
        indent = p_len - len(bb)
        for i, c in enumerate(bb):
            if c == '1':
                ret[i + indent] = 1
        return ret

    @staticmethod
    def _bits_binstr_to_list(s, p_len):
        """ Преобразование бин строки в список нулей и единиц """
        return IpRunProg.bits_int_to_list(int(s.hex(), 16), p_len)

    @staticmethod
    def bits_list(v, p_len):
        """ Преобразование числа или бин строки в список нулей и единиц """
        if type(v) is int:
            return IpRunProg.bits_int_to_list(v, p_len)
        elif type(v) is bytes:
            return IpRunProg._bits_binstr_to_list(v, p_len)
        else:
            raise IpRunError(f'допустимые типы: int, bytes; получен: {type(v).__name__}')

    @staticmethod
    def _list_to_str(lst, fmt):
        """ Преобразования значения из списка нулей и единиц в заданный формат (d, h, b) """
        n = int(''.join([str(n) for n in lst]), 2)
        if fmt == 'd':
            return str(n)
        elif fmt == 'b':
            ret = bin(n)
            if len(ret) - 2 < len(lst):
                ret = ret[:2] + '0' * (len(lst) - len(ret) + 2) + ret[2:]
            return ret
        else:
            ret = hex(n)
            if len(lst) % 4 == 0 and len(ret) - 2 < len(lst) // 4:
                ret = ret[:2] + '0' * (len(lst) // 4 - len(ret) + 2) + ret[2:]
            return ret

    @staticmethod
    def param_to_str(lst, fmt, delim=', '):
        """
            Преобразования значений параметров в строку с заданными форматами (d, h, b)
            пример формата: [(16, 'd'), (16, 'd')]
        """
        idx = 0
        ret = []
        for n, c in fmt:
            ret.append(IpRunProg._list_to_str(lst[idx: idx + n], c))
            idx += n
        return delim.join(ret)

    def run(self, func_name: str, params):
        """
            func_name: 'and:2:1'
            params: { 'param': ..., 'print_result': True }
            param: входной параметр; варианты: число, бин строка, список чисел или бин строк (соотв. формату параметра)
        """
        if params is None or 'param' not in params:
            raise IpRunError("не определён параметр params['param']; пример: { 'param': [1, 2] }")
        param = params['param']
        print_result = params.get('print_result', True)

        if func_name in self.prog.native_funcs:
            f: ProgFunc = self.prog.native_funcs[func_name]
        elif func_name in self.prog.funcs:
            f: ProgFunc = self.prog.funcs[func_name]
        else:
            raise IpRunError(f'функции {func_name} нет в этой программе')

        pp = []
        if type(param) is list:
            fmt = [n for n, _ in f.fmt[0]]
            if len(param) != len(fmt):
                raise IpRunError(f'получено {len(param)} параметров, должно быть {len(fmt)}')
            for i, n in enumerate(fmt):
                pp.extend(self.bits_list(param[i], n))
        else:
            pp = self.bits_list(param, f.len_in)

        rs = IpRunState(pp, f)
        f.runner.run(rs)

        ret = int(''.join([str(n) for n in rs.stack]), 2)

        if print_result:
            print(f'{func_name} ( {self.param_to_str(pp, f.fmt[0], ", ")} ) '
                  + f'-> {self.param_to_str(rs.stack, f.fmt[1], ", ")}')
        return ret
