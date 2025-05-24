
from typing import Dict
from mp_compiler_objects import Word, CompilerError


# =====================================================================================================================
class Prog:
    def __init__(self, runners):
        self.funcs = {}
        self.native_funcs = {}
        if runners:
            s = self.__class__.__name__
            if s not in runners:
                raise CompilerError(f'there is no corresponding runner for class {s}')
            self.runner = runners[s](self)
        else:
            self.runner = None

    def run(self, func_name: str, params=None):
        if self.runner is None:
            raise CompilerError('runners not defined')
        return self.runner.run(func_name, params)


# =====================================================================================================================
class ProgObject:
    def __init__(self, w_first: Word, runners):
        self.w_first = self.w_last = w_first
        if runners:
            s = self.__class__.__name__
            if s not in runners:
                raise CompilerError(f'there is no corresponding runner for class {s}')
            self.runner = runners[s](self)
        else:
            self.runner = Runner(self)

    # def run(self, rs):
    #     self.runner.run(rs)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.w_first}'


# =====================================================================================================================
class Runner:
    def __init__(self, po: ProgObject):
        self.po = po

    def run(self, rs):  # rs - run state
        raise CompilerError('run method is not implemented')

    def __str__(self):
        return f'{self.__class__.__name__}: {self.po}'


# =====================================================================================================================
class ProgFunc(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.descr = ''  # f:32:16
        self.name = ''  # f
        self.len_in = 0  # 32
        self.len_out = 0  # 16
        self.fmt_str = ''  # #16d+16d:16d
        self.fmt = ([], [])  # ([(16, 'd'), (16, 'd')],   [(16, 'd')])
        self.native = False
        self.block = ProgBlock(self.w_first, runners)
        self.vars: Dict[str:ProgVar] = {}
        self.called_func_names = []

    def __str__(self):
        w = self.w_first
        return f'{self.__class__.__name__}: "{w.word} {self.descr}" ({w.fname} {w.line_no}:{w.pos_no})'


# =====================================================================================================================
class ProgVar(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.descr = w_first.word
        ss = self.descr.split(':')
        self.name = ss[0]
        self.size = int(ss[1])
        self.used = False


# =====================================================================================================================
class ProgBlock(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.stack_len_in = self.stack_len_out = 0
        self.code = []  # list of executable instructions
        self.first_point = None  # first point in block; no points should be in loop block with depth change


# =====================================================================================================================
class ProgIf(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.block = ProgBlock(self.w_first, runners)
        self.block_else = None
        self.stack_len_in = self.stack_len_out = 0


# =====================================================================================================================
class ProgLoop(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.block = ProgBlock(self.w_first, runners)
        self.stack_len_in = self.stack_len_out = 0
        self.nn = 0


# =====================================================================================================================
class ProgReduce(ProgObject):
    def __init__(self, w_first: Word, nn, runners):
        super().__init__(w_first, runners)
        self.nn = nn  # the number of bits by which the stack depth is reduced


# =====================================================================================================================
class ProgAssign(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.var = None  # ProgVar or int
        self.is_num = False
        self.nn = 0  # number of bits (variable size)
        self.var_from_stack = False
        self.var_to_stack = False


# =====================================================================================================================
class ProgCall(ProgObject):
    def __init__(self, w_first: Word, runners):
        super().__init__(w_first, runners)
        self.f = None  # ProgFunc
