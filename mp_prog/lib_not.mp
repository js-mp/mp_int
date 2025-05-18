func not:1:1 {
  1:1>
  >xor:2:1>
}

func not:32:32 #32b:32b {
  def{ arg:32 }

  >arg:32 .

  loop 32 {
    arg:32> 0:1> >arg:32
    >not:1:1>
  }
}
