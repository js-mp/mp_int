func sum:3:2 {
  def{ a:1 b:1 c:1 }
  >c:1 >b:1 >a:1

  a:1> b:1> >and:2:1>
  b:1> c:1> >and:2:1>
  >or:2:1>
  a:1> c:1> >and:2:1>
  >or:2:1>

  a:1> b:1> >xor:2:1> c:1> >xor:2:1>
}

func sum:4:2 #2d+2d:2d {
  def{ arg1:2 arg2:2 x:1 ret:2 }

  >arg2:2 >arg1:2 .
  0:1> // carry bit

  loop 2 {
    0:1> arg1:2> >x:1 >arg1:2 x:1>
    0:1> arg2:2> >x:1 >arg2:2 x:1>
    >sum:3:2>
    ret:2> >_:1 >ret:2
  }

  >_:1 .
  ret:2>
}

func sum:16:8 #8d+8d:8d {
  def{ arg1:8 arg2:8 x:1 ret:8 }

  >arg2:8 >arg1:8 .
  0:1> // carry bit

  loop 8 {
    0:1> arg1:8> >x:1 >arg1:8 x:1>
    0:1> arg2:8> >x:1 >arg2:8 x:1>
    >sum:3:2>
    ret:8> >_:1 >ret:8
  }

  >_:1 .
  ret:8>
}

func sum:32:16 #16d+16d:16d {
  def{ arg1:16 arg2:16 x:1 ret:16 }

  >arg2:16 >arg1:16 .
  0:1> // carry bit

  loop 16 {
    0:1> arg1:16> >x:1 >arg1:16 x:1>
    0:1> arg2:16> >x:1 >arg2:16 x:1>
    >sum:3:2>
    ret:16> >_:1 >ret:16
  }

  >_:1 .
  ret:16>
}

func sum:64:32 #32d+32d:32d {
  def{ arg1:32 arg2:32 x:1 ret:32 }

  >arg2:32 >arg1:32 .
  0:1> // carry bit

  loop 32 {
    0:1> arg1:32> >x:1 >arg1:32 x:1>
    0:1> arg2:32> >x:1 >arg2:32 x:1>
    >sum:3:2>
    ret:32> >_:1 >ret:32
  }

  >_:1 .
  ret:32>
}
