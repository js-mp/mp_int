
from typing import List


# =====================================================================================================================
class CompilerError(Exception):
    def __init__(self, err):
        self.err = err if err != '' else 'error'

    def __str__(self):
        return self.err


# =====================================================================================================================
class Line:
    def __init__(self, fname, line_no, line, ss):
        self.fname = fname
        self.line_no = line_no
        self.line = line
        self.ss = ss

    def __str__(self):
        return f'{self.fname} {self.line_no}: {self.line}'

    def get_words(self):
        """ List of words of the line """
        ret: List[Word] = []
        p = 0
        for s in self.ss:
            p = self.line.find(s, p)
            if p < 0:
                raise CompilerError(f'{self.fname} {self.line_no}: word "{s}" not found in line: {self.line}')
            ret.append(Word(self.fname, self.line_no, p + 1, s))
            p += 1
        return ret


# =====================================================================================================================
class Word:
    def __init__(self, fname, line_no, pos_no, word):
        self.fname = fname
        self.line_no = line_no
        self.pos_no = pos_no
        self.word = word
        self.idx = -1  # will be filled lazily in get_w

    def __str__(self):
        return f'"{self.word}" ({self.fname} {self.line_no}:{self.pos_no})'


# =====================================================================================================================
class Warn:
    def __init__(self, w: Word, s: str):
        self.w = w
        self.s = s

    def __str__(self):
        return f'{self.w.fname} {self.w.line_no}:{self.w.pos_no} "{self.w.word}": {self.s}'


# =====================================================================================================================
class CompilerState:
    def __init__(self, ww: List[Word], prog, runners):
        self.ww = ww
        self.nn = len(ww)
        self.prog = prog
        self._warns: List[Warn] = []
        self.vars = {}  # имя -> ProgVar
        self._vars_stack = []
        self.stack_len = 0
        self.runners = runners if runners is not None else {}

    def get_words(self, from_idx: int):
        """ Generator for getting pairs (index, word) starting from the specified index """
        for i, w in enumerate(self.ww[from_idx:]):
            yield i + from_idx, w

    def print_warnings(self):
        if not self._warns:
            return
        print(f'\n{len(self._warns)} warnings:\n')
        for s in self._warns:
            print(f'{s}\n')

    def err(self, idx, s):
        w = self.ww[idx] if idx < self.nn else Word('???', 1, 1, '???')
        return CompilerError(str(Warn(w, s)))

    def warn(self, idx, s):
        w = self.ww[idx] if idx < self.nn else Word('???', 1, 1, '???')
        self._warns.append(Warn(w, s))

    def expect(self, idx, s):
        s1 = self.get_word(idx)
        if s1 != s:
            raise self.err(idx, f'expected "{s}", received "{s1}"')

    def get_w(self, idx):
        if idx < self.nn:
            w = self.ww[idx]
            w.idx = idx
            return w
        raise self.err(self.nn - 1, 'unexpected end of file')

    def get_word(self, idx):
        return self.get_w(idx).word

    def vars_push(self):
        self._vars_stack.append(self.vars.copy())

    def vars_pop(self):
        self.vars = self._vars_stack.pop()

    def check_stack_len(self, idx, min_len=0):
        if self.stack_len < min_len:
            raise self.err(idx, f'stack depth less than 0: {self.stack_len - min_len}')
