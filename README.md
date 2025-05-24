# MP Programming Language

MP is a domain-specific programming language designed for bit manipulation algorithms and generating corresponding logical expressions (implemented in a separate library).

## Key Features
- Focused on bit-level operations
- Supports structured programming with includes and functions
- Includes a set of native bitwise operations

## Language Restrictions
- Recursion is prohibited
- No conditional loops - all loops execute a fixed number of iterations

## Syntax Overview

### Includes
```mp
#include <filename>
```
(Note: Cannot be used inside function bodies)

### Native Functions
Native functions are predefined bitwise operations:
```mp
func and:2:1    #1d+1d:1d native   // Bitwise AND
func or:2:1     #1d+1d:1d native   // Bitwise OR
func xor:2:1    #1d+1d:1d native   // Bitwise XOR
func im:2:1     #1d+1d:1d native   // Implication ((not a) or b)
```

### Function Definition
```mp
func sum:16:8 #8d+8d:8d {
  // Function body
}
```
- `sum:16:8` - Function name with input (16 bits) and output (8 bits) sizes
- `#8d+8d:8d` - Optional format specification:
  - `d` - decimal
  - `h` - hexadecimal
  - `b` - binary

### Language Constructs
1. **Variable Declaration**:
```mp
def{ arg1:8 arg2:8 x:1 ret:8 }
```

2. **Stack Operations**:
   - Move to variable: `>arg1:8`
   - Push to stack: `x:1>`
   - Copy stack: `>arg1:8>`
   - Push constant: `27:8>` or `1B#h:8>` or `11011#b:8>`
   - Pop bits: `>_:8`

3. **Control Flow**:
   - Function call: `>sum:16:8>`
   - Stack check: `.` (zero-depth stack control, within this function; affects compilation but not execution; can be used for self-testing)
   - Loop: `loop 8 { ... }` (the loop body is executed a specified number of times, in this case 8)
   - Conditional: `if { ... } else { ... }` (one bit is popped from the stack, and if it is 1, the first block is executed, if 0, the second; the `else` block is optional; if specified, the stack depth change in both blocks must be the same)

4. **Comments**: `// Single-line comment`

## Examples

Run program:
```bash
./mp_run.py mp_prog/example_sum.mp sum:16:8 15 7
```

SHA-256 example:
```bash
./mp_run.py mp_prog/example_sha256.mp sha256:32:256 97 98 99 100
```

## Format Specifiers
- `d` - Decimal
- `h` - Hexadecimal
- `b` - Binary

Note: Only non-negative integers supported.


# Язык программирования MP

Язык программирования MP предназначен для описания алгоритмов манипуляции битами, с целью построения соответствующих
этим алгоритмам логических выражений (реализовано в отдельной библиотеке).

Ограничения языка, вытекающие из его предназначения:
1. Рекурсия запрещена.
2. Нет циклов с условиями; каждый цикл выполняется указанное количество раз.

Для структурирования программ предназначен оператор `#include <filename>` (не может использоваться в теле функций).

Для указания интерпретатору, какие функции являются элементарными, предназначены описания функция `native`.

Допустимые native-функции:
```
func and:2:1 #1d+1d:1d native
func or:2:1 #1d+1d:1d native
func xor:2:1 #1d+1d:1d native

func im:2:1 #1d+1d:1d native
```

Здесь `im` - это операция импликации: `im(a,b) = (not a) or b`. Её одной достаточно, чтобы определить
все другие битовые операции.

Пример определения функции:
```
func sum:16:8 #8d+8d:8d {
  ...
}
```

Здесь `sum:16:8` - это имя функции. Двоеточиями отделены число бит на входе и на выходе (в данном примере
функция принимает 16 бит и возвращает 8; вход берётся из стека, выход помещается в стек). После решетки `#`
идёт необязательное описание формата представления параметров и результата функции в программе mp_run.py;
знак плюс означает соединение нескольких параметров в один.

Типы форматов:
d - десятичное представление
h - шестнадцатиричное представление
b - двоичное представление
Допускаются только неотрицательные целые числа.

Можно определить несколько функций с одним собственным именем (до первого двоеточия), но разными размерами входных
и/или выходных параметров.

В теле функции можно использовать следующие операторы и синтаксические конструкции:
- описание локальных переменных: `def{ arg1:8 arg2:8 x:1 ret:8 }`; указывается имя переменной и её размер в битах;
  в отличии от функций, нельзя определить несколько переменных с одним собственным именем и разными размерами
- перемещение бит из стека в переменную: `>arg1:8`; глубина стека при этом уменьшается
- помещение бит из переменной в стек: `x:1>`; значение переменной при этом не меняется
- копирование бит из стека в переменную: `>arg1:8>`; глубина стека не меняется
- помещение в стек константы: `0:1>` - в стек добавляется один нулевой бит; константа может быть задана
  в десятичном `27`, шестнадцатиричном `1B#h` или двоичном `11011#b` виде
- удаление из стека заданного числа бит: `>_:8`
- вызов функции: `>sum:16:8>` - вызывается функция `sum:16:8`, ей в стеке передаётся 16 бит, и принимается 8;
  вызываемая функция должна быть описана до вызова
- контроль нулевой глубины стека (в рамках данной функции): `.` (точка); влияет на компиляцию, но не выполнение;
  можно использовать для самопроверки
- комментарии: `// ...`
- цикл: `loop 8 { ... }` - тело цикла выполняется заданное число раз (в данном случае 8)
- условное выполнение: `if { ... } else { ... }`; со стека извлекается один бит, и если это 1, то выполняется
  первый блок, если 0, то второй; блок `else` является необязательным; если он указан, то изменение глубины стека
  в обоих блоках должно быть одинаковым

  Примеры выполнения функций:

  ```
  ./mp_run.py mp_prog/example_sum.mp sum:16:8 15 7
  ```

  ```
  ./mp_run.py mp_prog/example_sha256.mp sha256:32:256 97 98 99 100
  ```
