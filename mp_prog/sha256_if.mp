#include libs_if.mp

func ki:0:2048 #0h:2048h { // table of constants k[i], direct order (extract by shift left)
  428A2F98#h:32> 71374491#h:32> B5C0FBCF#h:32> E9B5DBA5#h:32> 3956C25B#h:32> 59F111F1#h:32> 923F82A4#h:32> AB1C5ED5#h:32>
  D807AA98#h:32> 12835B01#h:32> 243185BE#h:32> 550C7DC3#h:32> 72BE5D74#h:32> 80DEB1FE#h:32> 9BDC06A7#h:32> C19BF174#h:32>
  E49B69C1#h:32> EFBE4786#h:32> 0FC19DC6#h:32> 240CA1CC#h:32> 2DE92C6F#h:32> 4A7484AA#h:32> 5CB0A9DC#h:32> 76F988DA#h:32>
  983E5152#h:32> A831C66D#h:32> B00327C8#h:32> BF597FC7#h:32> C6E00BF3#h:32> D5A79147#h:32> 06CA6351#h:32> 14292967#h:32>
  27B70A85#h:32> 2E1B2138#h:32> 4D2C6DFC#h:32> 53380D13#h:32> 650A7354#h:32> 766A0ABB#h:32> 81C2C92E#h:32> 92722C85#h:32>
  A2BFE8A1#h:32> A81A664B#h:32> C24B8B70#h:32> C76C51A3#h:32> D192E819#h:32> D6990624#h:32> F40E3585#h:32> 106AA070#h:32>
  19A4C116#h:32> 1E376C08#h:32> 2748774C#h:32> 34B0BCB5#h:32> 391C0CB3#h:32> 4ED8AA4A#h:32> 5B9CCA4F#h:32> 682E6FF3#h:32>
  748F82EE#h:32> 78A5636F#h:32> 84C87814#h:32> 8CC70208#h:32> 90BEFFFA#h:32> A4506CEB#h:32> BEF9A3F7#h:32> C67178F2#h:32>
}

func prep_msg:16:512 #16h:512h {
  1:1> 0:431> 16:64>
}

func prep_msg:1:512 #1h:512h {
  1:1> 0:446> 1:64>
}

func prep_msg:64:512 #64h:512h {
  1:1> 0:383> 64:64>
}

func prep_msg:32:512 #32d:512h {
  1:1> 0:415> 32:64>
}

func hh_init:0:256 {
  6A09E667BB67AE853C6EF372A54FF53A510E527F9B05688C1F83D9AB5BE0CD19#h:256>
}

func get_w2:512:544 {
  def { tmp:64 } // 32*2
  >tmp:64> tmp:64> >_:32 // 32*(2-1)
}

func get_w7:512:544 {
  def { tmp:224 } // 32*7
  >tmp:224> tmp:224> >_:192 // 32*(7-1)
}

func get_w15:512:544 {
  def { tmp:480 } // 32*15
  >tmp:480> tmp:480> >_:448 // 32*(15-1)
}

func get_w16:512:544 {
  def { tmp:512 } // 32*16
  >tmp:512> tmp:512> >_:480 // 32*(16-1)
}

func add_msg:512:2048 {
  def { w15:32 w2:32 w16:32 w7:32 s0:32 s1:32 }

  loop 48 {
    >get_w2:512:544> >w2:32
    >get_w7:512:544> >w7:32
    >get_w15:512:544> >w15:32
    >get_w16:512:544> >w16:32
    w15:32> >rotr7:32:32> w15:32> >rotr18:32:32> >xor:64:32> w15:32> >shr3:32:32> >xor:64:32> >s0:32
    w2:32> >rotr17:32:32> w2:32> >rotr19:32:32> >xor:64:32> w2:32> >shr10:32:32> >xor:64:32> >s1:32
    w16:32> s0:32> >sum:64:32> w7:32> >sum:64:32> s1:32> >sum:64:32>
  }
}

func sha_block:768:256 #512h+256h:256h { // input: 512-bit block, 256-bit hash (h[i]); output: hash
  def { a:32 b:32 c:32 d:32 e:32 f:32 g:32 h:32 }
  def { S0:32 Ma:32 t2:32 S1:32 Ch:32 t1:32 }
  def { kk:2048 ww:2048 hh:256 hh1:256 }

  >hh:256> >hh1:256
  >add_msg:512:2048> >ww:2048 .
  >ki:0:2048> >kk:2048 .

  hh:256> 0:32> >hh:256 >a:32 .
  hh:256> 0:32> >hh:256 >b:32 .
  hh:256> 0:32> >hh:256 >c:32 .
  hh:256> 0:32> >hh:256 >d:32 .
  hh:256> 0:32> >hh:256 >e:32 .
  hh:256> 0:32> >hh:256 >f:32 .
  hh:256> 0:32> >hh:256 >g:32 .
  hh:256> 0:32> >hh:256 >h:32 .

  loop 64 {
    a:32> >rotr2:32:32> a:32> >rotr13:32:32> a:32> >rotr22:32:32> >xor:64:32> >xor:64:32> >S0:32 .
    a:32> b:32> >and:64:32> a:32> c:32> >and:64:32> b:32> c:32> >and:64:32> >xor:64:32> >xor:64:32> >Ma:32 .
    Ma:32> S0:32> >sum:64:32> >t2:32 .
    e:32> >rotr6:32:32> e:32> >rotr11:32:32> e:32> >rotr25:32:32> >xor:64:32> >xor:64:32> >S1:32 .
    e:32> f:32> >and:64:32> e:32> >not:32:32> g:32> >and:64:32> >xor:64:32> >Ch:32 .
    kk:2048> 0:32> >kk:2048
    ww:2048> 0:32> >ww:2048
    h:32> S1:32> Ch:32>
    >sum:64:32> >sum:64:32> >sum:64:32> >sum:64:32> >t1:32 .
    g:32> >h:32 .
    f:32> >g:32 .
    e:32> >f:32 .
    d:32> t1:32> >sum:64:32> >e:32 .
    c:32> >d:32 .
    b:32> >c:32 .
    a:32> >b:32 .
    t1:32> t2:32> >sum:64:32> >a:32 .
  }

  hh:256> hh1:256> 0:32> >hh1:256 a:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 b:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 c:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 d:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 e:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 f:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 g:32> >sum:64:32> >hh:256 >_:32 .
  hh:256> hh1:256> 0:32> >hh1:256 h:32> >sum:64:32> >hh:256 >_:32 .

  hh:256>
}

func sha:32:256 #32d:256h {
  >prep_msg:32:512> >hh_init:0:256> >sha_block:768:256>
}

func sha:64:256 #64h:256h {
  >prep_msg:64:512> >hh_init:0:256> >sha_block:768:256>
}

func sha:16:256 #16h:256h {
  >prep_msg:16:512> >hh_init:0:256> >sha_block:768:256>
}

func sha:1:256 #1h:256h {
  >prep_msg:1:512> >hh_init:0:256> >sha_block:768:256>
}

func prep_msg:2:512 #2h:512h {
  1:1> 0:445> 1:64>
}

func sha:2:256 #2h:256h {
  >prep_msg:2:512> >hh_init:0:256> >sha_block:768:256>
}
