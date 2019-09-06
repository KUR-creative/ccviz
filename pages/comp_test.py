# map <F5> :wa<CR>:!pytest -vv pages/comp_test.py<CR>
from pages.comp import sync_tok, sync_li2, split_nls

def test_sync_tok__pad_space():
    a,b = sync_tok('123', 'abc ')
    assert len(a) == len(b)
    assert a == '123 '

def test_sync_tok__pad_last_newline_chars__if_a_has_last_newline_chars():
    a,b = sync_tok('123\n\n', '123xa')
    assert len(a) == len(b)
    assert a == '123  \n\n'
    assert b == '123xa\n\n'

def test_sync_tok__pad_last_newline_chars__if_a_has_last_newline_chars2():
    a,b = sync_tok(' 123-219  \n\n\n', '123xa')
    assert len(a) == len(b)
    assert a == ' 123-219  \n\n\n'
    assert b == '123xa     \n\n\n'


def test_sync_li2__len_src_greater_than_len_dst():
    assert sync_li2([1,2,3], [1,2], modify_left=True)  == [2,3]
    assert sync_li2([1,2,3], [1,2], modify_left=False) == [1,2]
    assert sync_li2([1,2],   [],    modify_left=True, padval=0) == []
def test_sync_li2__len_src_smaller_than_len_dst():
    assert sync_li2([1,2], [1,2,3,4],   modify_left=True,  padval=0) == [0,0,1,2]
    assert sync_li2((1,2), [1,2,3,4,5], modify_left=False, padval=0) == (1,2,0,0,0)
    assert sync_li2([],    [1,2,3,4],   modify_left=True,  padval=0) == [0,0,0,0]
def test_sync_li2__len_src_is_same_to_len_dst():
    assert sync_li2([1,2], [1,2], modify_left=True, padval=0) == [1,2]
    assert sync_li2([],    [],    modify_left=True, padval=0) == []


def test_split_nls_no_nl():
    assert split_nls(('asdwec',-1)) == [('asdwec',-1)]
def test_split_nls_1_nl():
    assert split_nls(('asdwec\n',-1)) == [('asdwec',-1), ('\n',None)]
def test_split_nls_N_nl():
    assert split_nls(('asec\n\n',-1)) == [('asec',-1), ('\n',None), ('\n',None)]
    assert split_nls(('asdwec\n\n\n',-1)) == [('asdwec',-1), ('\n',None), ('\n',None), ('\n',None)]
def test_split_nls_1_nl_with_padnote():
    assert split_nls(('asdwec\n',-1),'padnote') == [('asdwec',-1), ('\n','padnote')]
