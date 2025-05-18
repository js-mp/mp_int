func mul:32:32 #16d+16d:32d {
  def{ arg1:16 arg22:16 arg2:32 x:1 ret:32 }

  >arg22:16 >arg1:16 .
  0:16> arg22:16> >arg2:32 .
  
  loop 16 {
    0:1> arg1:16> >x:1 >arg1:16 x:1>
    if {
      ret:32> arg2:32> >sum:64:32> >ret:32
    }
    arg2:32> 0:1> >arg2:32 >_:1 .
  }

  ret:32>
}
