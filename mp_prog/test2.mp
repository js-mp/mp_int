func not:1:1 {
  if {
    0:1>
  } else {
    1:1>
  }
}

func not:8:8 {
  def { arg:8 }
  >arg:8
  loop 8 {
    arg:8> 0:1> >arg:8 >not:1:1>
  }
}
