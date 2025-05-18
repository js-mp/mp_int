func xor:64:32 #32b+32b:32b {
  def{ arg1:32 arg2:32 }

  >arg2:32 >arg1:32 .

  loop 32 {
    arg1:32> 0:1> >arg1:32
    arg2:32> 0:1> >arg2:32
    >xor:2:1>
  }
}
