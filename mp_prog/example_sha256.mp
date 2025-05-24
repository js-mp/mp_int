#include sha256_native.mp

// вычисление sha256 для строки из 4 символов ascii (задаются своими кодами)
func sha256:32:256 #8d+8d+8d+8d:256h {
  >sha:32:256>
}

// пример использования (строка 'abcd'):
// ./mp_run.py mp_prog/example_sha256.mp sha256:32:256 97 98 99 100
