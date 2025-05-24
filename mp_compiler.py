
import os
from mp_compiler_objects import *
from mp_prog_objects import *


# =====================================================================================================================
class Compiler:
    def __init__(self, mp_file_name, runners=None):
        fname = os.path.abspath(mp_file_name)
        self._mp_file_name = os.path.basename(fname)
        self._mp_file_dir = os.path.dirname(fname) + os.path.sep
        self._fnames = set()
        self.fnames: List[str] = []
        self.lines: List[Line] = []
        self.prog = None
        self.runners = runners

    def __str__(self):
        return f'compiled: {self._mp_file_dir}{self._mp_file_name} ({len(self.fnames)} files; {len(self.lines)} lines)'

    def _clear_state(self):
        self._fnames.clear()
        self.fnames.clear()
        self.lines.clear()
        self.prog = None

    def _read_lines(self, fname):
        self._fnames.add(fname)
        self.fnames.append(fname)

        ret: List[Line] = []
        line_no = 0
        with open(self._mp_file_dir + fname) as f:
            ss = [s.rstrip() for s in f.readlines()]

        for line in ss:
            line_no += 1
            s = line
            comment_pos = s.find('//')
            if comment_pos >= 0:
                s = s[:comment_pos]
            if '#include' in s:
                s = s.strip()[8:].lstrip()  # file name in #include statement
                if os.path.sep in s:
                    self._clear_state()
                    raise CompilerError(f'{fname} {line_no}: the file name must not contain a separator: {s}')
                if s in self._fnames:
                    self._clear_state()
                    raise CompilerError(f'{fname} {line_no}: recursive file reference {s}')
                ret.extend(self._read_lines(s))
            else:
                for s1, s2 in [('.', ' . '), ('{', ' { '), ('}', ' } ')]:
                    s = s.replace(s1, s2)
                ww = s.split()
                ret.append(Line(fname, line_no, line, ww))

        self._fnames.remove(fname)
        return ret

    def get_words(self):
        """ List of words of the entire program """
        if len(self.lines) == 0:
            self.read_prog()
        ret: List[Word] = []
        for s in self.lines:
            ret.extend(s.get_words())
        return ret

    def read_prog(self):
        self._clear_state()
        self.lines.extend(self._read_lines(self._mp_file_name))

    def compile(self, print_warnings=True):
        self.read_prog()
        ww = self.get_words()
        if len(ww) == 0:
            raise CompilerError('empty program')
        self.prog = Prog(self.runners)
        cs = CompilerState(ww, self.prog, self.runners)
        idx = 0
        while idx < cs.nn:
            f = ProgFunc(cs.get_w(idx), cs.runners)
            idx = self.compile_func(cs, f)
        if print_warnings:
            cs.print_warnings()
        self._check_recursion(cs)
        return self.prog

    def _check_recursion(self, cs):
        # in fact, recursion can only occur when calling itself
        for f in self.prog.funcs.values():
            prev_len = 0
            nn = set(f.called_func_names)
            add = set()
            while len(nn) > prev_len:
                prev_len = len(nn)
                add.clear()
                for s in f.called_func_names:
                    add |= set(self.prog.funcs[s].called_func_names)
                nn |= add
            if f.descr in nn:
                idx = f.w_first.idx + 1
                raise CompilerError(str(Warn(cs.ww[idx], 'recursive function call')))

    @staticmethod
    def is_valid_name(s: str):
        return s[0].isalpha() and s.isidentifier() and s.isascii()

    @staticmethod
    def compile_func(cs: CompilerState, f: ProgFunc):
        # declaration of function func
        idx = f.w_first.idx
        cs.vars = {}
        cs.stack_len = 0

        cs.expect(idx, 'func')
        idx += 1

        # function f:32:16 declaration
        f.descr = cs.get_word(idx)
        ss = f.descr.split(':')
        if len(ss) != 3 or not ss[1].isdecimal() or not ss[2].isdecimal():
            raise cs.err(idx, 'invalid function declaration (example: f:32:16)')
        f.name = ss[0]
        f.len_in = int(ss[1])
        f.len_out = int(ss[2])
        cs.stack_len = f.len_in
        if not Compiler.is_valid_name(f.name):
            raise cs.err(idx, f'Invalid function name "{f.name}"')
        elif f.len_out == 0:
            raise cs.err(idx, 'the number of output bits cannot be zero')
        elif f.descr in cs.prog.native_funcs:
            raise cs.err(idx, f'function {f.descr} already exists among native functions')
        elif f.descr in cs.prog.funcs:
            raise cs.err(idx, f'function {f.descr} already exists among the described functions')
        idx += 1

        # Parameter format #16d+16d:16d
        w = cs.get_w(idx)
        if w.word in ('{', 'native'):
            f.fmt_str = f'#{f.len_in}h:{f.len_out}h'
            idx -= 1
        else:
            f.fmt_str = w.word
        if f.fmt_str[0] != '#':
            raise cs.err(idx, 'expected parameter format ("#16d+16d:16d")')
        ss = f.fmt_str[1:].split(':')
        valid = True
        if len(ss) != 2:
            valid = False
        if valid:
            s1 = ss[0].split('+')
            s2 = ss[1].split('+')
            for s in s1 + s2:
                if len(s) < 2 or s[-1] not in 'dhb' or not s[:-1].isdecimal():
                    valid = False
                    break
            if valid:
                n = 0
                for s in s1:
                    f.fmt[0].append((int(s[:-1]), s[-1]))
                    n1 = f.fmt[0][-1][0]
                    n += n1
                    if n1 == 0 and f.len_in > 0:
                        raise cs.err(idx, 'zero length is not allowed')
                if n != f.len_in:
                    raise cs.err(idx, f'mismatch between length of input parameter {f.len_in} and format {n}')
                n = 0
                for s in s2:
                    f.fmt[1].append((int(s[:-1]), s[-1]))
                    n1 = f.fmt[1][-1][0]
                    n += n1
                    if n1 == 0:
                        raise cs.err(idx, 'zero length is not allowed')
                if n != f.len_out:
                    raise cs.err(idx, f'mismatch between length of output parameter {f.len_out} and format {n}')
        if not valid:
            raise cs.err(idx, 'invalid parameter format (example: #16d+16d:16d)')
        idx += 1

        w = cs.get_w(idx)
        if w.word == 'native':
            f.native = True
            f.w_last = w
            cs.prog.native_funcs[f.descr] = f
            return idx + 1
        elif w.word == '{':
            cs.prog.funcs[f.descr] = f
        else:
            raise cs.err(idx, 'expected "native" or "{"')

        # parsing a function block
        f.block.w_first = f.block.w_last = w
        idx = Compiler.compile_block(cs, f, f.block)

        f.w_last = cs.get_w(idx - 1)
        if cs.stack_len != f.len_out:
            raise cs.err(idx - 1, f'required stack depth {cs.stack_len} differs from actual {f.len_out}')
        f.called_func_names = list(set(f.called_func_names))
        f.called_func_names.sort()

        Compiler._check_used_vars(cs, f)

        return idx

    @staticmethod
    def _check_used_vars(cs: CompilerState, f: ProgFunc):
        for v in f.vars.values():
            if not v.used:
                cs.warn(v.w_first.idx, 'variable is not used')

    @staticmethod
    def compile_def(cs: CompilerState, f: ProgFunc, idx: int):
        """ Parsing variable declarations """
        cs.expect(idx, 'def')
        idx += 1
        cs.expect(idx, '{')
        idx += 1
        while cs.get_word(idx) != '}':
            w = cs.get_w(idx)
            ss = w.word.split(':')
            if len(ss) != 2 or not Compiler.is_valid_name(ss[0]) or not ss[1].isdecimal():
                raise cs.err(idx, 'invalid variable description format (example: v:32)')
            v = ProgVar(w, cs.runners)
            if v.size == 0:
                raise cs.err(idx, 'zero size is not allowed')
            elif v.name in f.vars:
                raise cs.err(idx, 'a variable with that name is already declared in this function')
            f.vars[v.name] = v
            cs.vars[v.name] = v
            idx += 1
        return idx + 1

    @staticmethod
    def compile_if(cs: CompilerState, f: ProgFunc, x: ProgIf):
        idx = x.w_first.idx
        cs.check_stack_len(idx, 1)
        x.stack_len_in = cs.stack_len
        cs.stack_len -= 1
        stack_len = cs.stack_len
        idx += 1

        w = cs.get_w(idx)
        x.block.w_first = x.block.w_last = w
        idx = Compiler.compile_block(cs, f, x.block)
        x.w_last = cs.get_w(idx - 1)
        x.stack_len_out = cs.stack_len

        if cs.get_word(idx) == 'else':
            idx += 1
            x.block_else = ProgBlock(cs.get_w(idx), cs.runners)
            cs.stack_len = stack_len
            idx = Compiler.compile_block(cs, f, x.block_else)
            x.w_last = cs.get_w(idx - 1)
            if x.stack_len_out != cs.stack_len:
                raise cs.err(idx, f'stack depth after if and else is different: {x.stack_len_out} != {cs.stack_len}')
        return idx

    @staticmethod
    def compile_loop(cs: CompilerState, f: ProgFunc, x: ProgLoop):
        idx = x.w_first.idx
        x.stack_len_in = cs.stack_len
        idx += 1

        w = cs.get_w(idx)
        if not w.word.isdecimal():
            raise cs.err(idx, 'expected number of cycle repetitions')
        x.nn = int(w.word)
        if x.nn < 2:
            cs.warn(idx, f'number of cycle repetitions: {x.nn}')
        idx += 1

        w = cs.get_w(idx)
        x.block.w_first = x.block.w_last = w
        idx = Compiler.compile_block(cs, f, x.block)
        x.w_last = cs.get_w(idx - 1)

        x.stack_len_out = x.stack_len_in + (x.block.stack_len_out - x.block.stack_len_in) * x.nn
        cs.stack_len = x.stack_len_out
        cs.check_stack_len(idx - 1, 0)

        if x.block.first_point is not None and x.block.stack_len_out != x.block.stack_len_in:
            n = x.block.stack_len_out - x.block.stack_len_in
            raise cs.err(idx, f'depth control (dot) in loop with stack depth change (by {n})')

        return idx

    @staticmethod
    def compile_reduce(cs: CompilerState, x: ProgReduce):
        idx = x.w_first.idx
        w = cs.get_w(idx)

        if w.word[:3] != '>_:' or not w.word[3:].isdecimal():
            raise cs.err(idx, 'invalid stack depth reduction command (example: >_:16)')

        x.nn = int(w.word[3:])
        if x.nn == 0:
            cs.warn(idx, 'zero stack depth change')

        cs.stack_len -= x.nn
        cs.check_stack_len(idx, 0)

        idx += 1
        return idx

    @staticmethod
    def compile_assign(cs: CompilerState, x: ProgAssign):
        idx = x.w_first.idx
        w = cs.get_w(idx)

        s = w.word
        if s[0] == '>':
            x.var_from_stack = True
            s = s[1:]
        if s[-1] == '>':
            x.var_to_stack = True
            s = s[:-1]
        ss = s.split(':')
        if len(ss) != 2 or ss[0] == '' or not ss[1].isdecimal():
            raise cs.err(idx, 'invalid assignment command (examples: >v:16 v:16> >v:16>)')

        x.nn = int(ss[1])
        x.var = ss[0]  # variable name or constant
        x.is_num = x.var[0].isdecimal() or '#' in x.var

        if x.is_num:
            fmt = 'd'
            if x.var.count('#') == 1:
                ss = x.var.split('#')
                x.var = ss[0]
                fmt = ss[1]
            fmt = 10 if fmt == 'd' else 16 if fmt == 'h' else 2 if fmt == 'b' else 0
            if fmt == 0:
                raise cs.err(idx, 'invalid number system designation (valid: d, h, b)')

            try:
                x.var = int(x.var, fmt)
            except ValueError:
                raise cs.err(idx, 'invalid representation of constant')

            if x.var_from_stack:
                raise cs.err(idx, 'writing from the stack to a constant is impossible')
            elif not x.var_to_stack:
                raise cs.err(idx, 'constant can only be written to the stack')
            n = len(bin(x.var)) - 2
            if n > x.nn:
                raise cs.err(idx, f'the specified size ({x.nn}) cannot be less than the size of the constant in bits ({n})')
        else:
            if x.var not in cs.vars:
                raise cs.err(idx, f'variable "{x.var}" is not defined')
            x.var = cs.vars[x.var]
            x.var.used = True

        if not x.is_num and x.var.size != x.nn:
            raise cs.err(idx, f'the size of the variable {x.var.size} does not match the specified size {x.nn}')
        elif x.nn == 0:
            raise cs.err(idx, 'variable size cannot be zero')

        if x.var_from_stack:
            cs.stack_len -= x.nn
        if x.var_to_stack:
            cs.stack_len += x.nn
        cs.check_stack_len(idx, 0)

        idx += 1
        return idx

    @staticmethod
    def compile_call(cs: CompilerState, f: ProgFunc, x: ProgCall):
        idx = x.w_first.idx
        w = cs.get_w(idx)

        if w.word[0] != '>' or w.word[-1] != '>':
            raise cs.err(idx, 'Invalid function call command (example: >f:32:16>)')
        s = w.word[1:-1]

        if s in cs.prog.native_funcs:
            x.f = cs.prog.native_funcs[s]
        elif s in cs.prog.funcs:
            x.f = cs.prog.funcs[s]
            f.called_func_names.append(s)
        if x.f is None:
            raise cs.err(idx, f'function "{s}" is not defined')

        cs.stack_len += x.f.len_out - x.f.len_in
        cs.check_stack_len(idx, 0)

        idx += 1
        return idx

    @staticmethod
    def compile_block(cs: CompilerState, f: ProgFunc, b: ProgBlock):
        """ Parsing a block """
        idx = b.w_first.idx
        cs.expect(idx, '{')
        cs.vars_push()
        b.stack_len_in = cs.stack_len
        idx += 1

        while cs.get_word(idx) != '}':
            w = cs.get_w(idx)

            if w.word == '.':  # stack depth check: must be 0
                if cs.stack_len != 0:
                    raise cs.err(idx, f'stack depth is not 0: {cs.stack_len}')
                if b.first_point is None:
                    b.first_point = w
                idx += 1
            elif w.word == 'def':
                idx = Compiler.compile_def(cs, f, idx)
            elif w.word == 'if':
                x = ProgIf(w, cs.runners)
                b.code.append(x)
                idx = Compiler.compile_if(cs, f, x)
            elif w.word == 'loop':
                x = ProgLoop(w, cs.runners)
                b.code.append(x)
                idx = Compiler.compile_loop(cs, f, x)
            elif w.word == '>>_':  # decrease stack depth to zero
                x = ProgReduce(w, cs.stack_len, cs.runners)
                b.code.append(x)
                cs.stack_len = 0
                idx += 1
            elif w.word[:3] == '>_:':  # decrease stack depth by a given amount
                x = ProgReduce(w, 0, cs.runners)
                b.code.append(x)
                idx = Compiler.compile_reduce(cs, x)
            elif '>' in w.word and w.word.count(':') == 1:  # assignment
                x = ProgAssign(w, cs.runners)
                b.code.append(x)
                idx = Compiler.compile_assign(cs, x)
            elif '>' in w.word and w.word.count(':') == 2:  # function call
                x = ProgCall(w, cs.runners)
                b.code.append(x)
                idx = Compiler.compile_call(cs, f, x)
            else:
                raise cs.err(idx, 'unknown or unexpected operator')
        idx += 1

        b.stack_len_out = cs.stack_len
        cs.vars_pop()
        return idx
