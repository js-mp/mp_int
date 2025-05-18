
func im:2:1 #1d+1d:1d native

func or:2:1 #1d+1d:1d {
  def { x:1 }
  >x:1
  0:1> >im:2:1>
  x:1> >im:2:1>
}

func and:2:1 #1d+1d:1d {
  def { x:1 y:1 }
  >x:1
  0:1> >im:2:1>
  >y:1 x:1> y:1> >im:2:1>
  0:1> >im:2:1>
}

func xor:2:1 #1d+1d:1d {
  def { x:1 y:1 }
  >y:1 >x:1
  x:1> y:1> >im:2:1>
  y:1> x:1> >im:2:1> 0:1> >im:2:1>
  >im:2:1>
}
