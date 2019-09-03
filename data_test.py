# map <F5> :wa<CR>:!pytest -vv data_test.py<CR>
import data
import file_utils as fu

def test_code__no_empty_line__no_head_spacing(tmp_path):
    raw_code = '#include "firm.h"\n#include "memory.h"\n#include "cache.h"'
    tmp_srcpath = tmp_path/'Formatted_A'/'A'/'src.c' 
    tmp_mappath = tmp_path/'Token_A'/'A'/'src.cmap' 

    fu.write_text(tmp_srcpath, raw_code)
    fu.write_text(tmp_mappath, '1 10 \n1 10\n1 10\n') 

    assert data.code('A', 0, str(tmp_srcpath)).raw == raw_code
