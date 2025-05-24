#include sha256_native.mp

// sha256 calculation for a string of 4 ascii characters (specified by their codes)
func sha256:32:256 #8d+8d+8d+8d:256h {
  >sha:32:256>
}

// usage example (for string 'abcd'):
// ./mp_run.py mp_prog/example_sha256.mp sha256:32:256 97 98 99 100
