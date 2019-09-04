# map <F5> :wa<CR>:!pytest -vv data_test.py<CR>
# map <F7> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/arm9_11; python main.py fixture/tmp-matching-window/arm9_11/strong_link/164.125.34.91_2019-08-30-12-34-29.zip -a 10 -r 0.1 -o tmp-result/tmp-matching-window/arm9_11/strong_link<CR>
# map <F8> :wa<CR>:!rm -rf tmp2/;python main.py fixture/tmp-matching-window/ms/164.125.34.91_2019-08-30-12-40-03.zip -o tmp-result/tmp-matching-window/ms<CR>
import data
import file_utils as fu

def test_code__no_empty_line__no_head_spacing(tmp_path):
    raw_code = '#include "firm.h"\n#include "memory.h"\n#include "cache.h"'
    tmp_srcpath = tmp_path/'Formatted_A'/'A'/'src.c' 
    tmp_mappath = tmp_path/'Token_A'/'A'/'src.cmap' 

    fu.write_text(tmp_srcpath, raw_code)
    fu.write_text(tmp_mappath, '1 10 \n1 10\n1 10\n') 

    code = data.code('A', 0, str(tmp_srcpath))
    assert code.raw == raw_code
    assert code.tokens == (
        '#include ', '"firm.h"\n',
        '#include ', '"memory.h"\n',
        '#include ', '"cache.h"'
    )

#def test_code__no_empty_line__head_spacing
#def test_code__empty_line__no_head_spacing
#def test_code__empty_line__head_spacing
