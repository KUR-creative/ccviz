# map <F5> :wa<CR>:!pytest -vv pages/comp_test.py<CR>
import pages.comp

def test_sync_tok__pad_space():
    a,b = pages.comp.sync_tok('123', 'abc ')
    assert len(a) == len(b)
    assert a == '123 '

def test_sync_tok__pad_last_newline_chars__if_a_has_last_newline_chars():
    a,b = pages.comp.sync_tok('123\n\n', '123xa')
    assert len(a) == len(b)
    assert a == '123  \n\n'
    assert b == '123xa\n\n'

def test_sync_tok__pad_last_newline_chars__if_a_has_last_newline_chars2():
    a,b = pages.comp.sync_tok(' 123-219  \n\n\n', '123xa')
    assert len(a) == len(b)
    assert a == ' 123-219  \n\n\n'
    assert b == '123xa     \n\n\n'


from pages.comp import sync_list2
def test_sync_lists__len_src_greater_than_len_dst():
    assert sync_list2([1,2,3], [1,2], modify_left=True, 0) == [2,3]
