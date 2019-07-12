import funcy as F
import itertools as I

tup = lambda f: lambda argtup: f(*argtup)
go = lambda x,*fs: F.rcompose(*fs)(x)
pipe = F.rcompose

from collections import namedtuple
def prop(p, obj=None):
    return(getattr(obj, p) if (isinstance(obj,tuple) and 
                               isinstance(p,str))
      else obj[p] if hasattr(obj,'__getitem__')
      else getattr(obj, p) if obj 
      else lambda o: prop(p,o))

def unzip(seq):
    return zip(*seq)

def map(f,*seq):
    return F.map(f,*seq) if seq \
    else lambda *xs: F.map(f,*xs)
def lmap(f,*seq):
    return F.lmap(f,*seq) if seq \
    else lambda *xs: F.lmap(f,*xs)

def filter(f,*seq):
    return F.filter(f,*seq) if seq \
    else lambda *xs: F.filter(f,*xs)
def lfilter(f,*seq):
    return F.lfilter(f,*seq) if seq \
    else lambda *xs: F.lfilter(f,*xs)

def starmap(f,*seq):
    return I.starmap(f,*seq) if seq \
    else lambda *xs: I.starmap(f,*xs)
def lstarmap(f,*seq):
    return list(I.starmap(f,*seq)) if seq \
    else lambda *xs: list(I.starmap(f,*xs))

def foreach(f,*seq):
    F.lmap(f,*seq)
    return None

class A():
    def __init__(self,x): self.x = x
    def m(self,x): return x

if __name__ == '__main__':
    print( lmap(tup(pow))( [(2,5),(3,2),(10,3)] ) )
    print( list(starmap(pow)([(2,5),(3,2),(10,3)] ) ))
    print( lstarmap(pow)([(2,5),(3,2),(10,3)] ) )

    print( list(map(tup(pow))( [(2,5),(3,2),(10,3)] ) ))

    print(F.lmap(
        lambda a,b,c: a+b+c, [1,2,3],[2,3,4],[5,6,7]
    ))

    a = A(2)
    assert 1 == prop(0, {0:1})
    assert '1' == prop(0, {0:'1'})
    assert 2 == prop('x', a)
    assert 0 == prop('m', a)(0)

    assert 1 == prop(0)({0:1})
    assert '1' == prop(0)({0:'1'})
    assert 2 == prop('x')(a)
    assert 0 == prop('m')(a)(0)

    assert 'a' == prop(0,'abcd')
    assert 'a' == prop(0,['a','bcd'])

    #namedtuple special rule
    X = namedtuple('X', 'a b c d')
    x = X(1,'b',d='123',c=56.2)
    assert 1     == prop(0,x)
    assert 'b'   == prop('b',x)
    assert '123' == prop('d',x)
    assert 56.2  == prop(2,x), prop(2,x)
