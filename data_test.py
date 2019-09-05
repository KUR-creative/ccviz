# map <F5> :wa<CR>:!pytest -vv data_test.py<CR>
# map <F7> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/arm9_11; python main.py fixture/tmp-matching-window/arm9_11/strong_link/164.125.34.91_2019-08-30-12-34-29.zip -a 10 -r 0.1 -o tmp-result/tmp-matching-window/arm9_11/strong_link<CR>
# map <F8> :wa<CR>:!rm -rf tmp2/;python main.py fixture/tmp-matching-window/ms/164.125.34.91_2019-08-30-12-40-03.zip -o tmp-result/tmp-matching-window/ms<CR>
import data
import file_utils as fu

def test_code__no_empty_line__no_head_spacing(tmp_path):
    # given
    raw_code = '#include "firm.h"\n#include "memory.h"\n#include "cache.h"'
    tmp_srcpath = tmp_path/'Formatted_A'/'A'/'ExHx.c' 
    tmp_mappath = tmp_path/'Token_A'/'A'/'ExHx.cmap' 

    fu.write_text(tmp_srcpath, raw_code)
    fu.write_text(tmp_mappath, '1 10 \n1 10\n1 10\n') 

    # when
    code = data.code('A', 0, str(tmp_srcpath))

    # then
    assert code.raw == raw_code
    assert code.tokens == (
        '#include ', '"firm.h"\n',
        '#include ', '"memory.h"\n',
        '#include ', '"cache.h"'
    )

def test_code__no_empty_line__head_spacing(tmp_path):
    # given
    raw_code =('void main( Firm * firm, bool isNand ) {\n'
             + '  u32 argc;\n'
             + '  char * argv[2];\n'
             + '  struct fb fbs[2] = {\n'
             + '    {\n') # TODO: last '\n' have to do not affect result
    tmp_srcpath = tmp_path/'Formatted_A'/'A'/'ExHo.c' 
    tmp_mappath = tmp_path/'Token_A'/'A'/'ExHo.cmap' 

    fu.write_text(tmp_srcpath, raw_code)
    fu.write_text(
        tmp_mappath, 
        '1 12 17 19 25 30 38 \n'
      + '3 7 \n'
      + '3 8 10 \n'
      + '3 10 13 20 22 \n'
      + '5\n')

    # when
    code = data.code('A', 0, str(tmp_srcpath))

    # then
    assert code.raw == raw_code
    assert code.tokens == (
        'void main( ','Firm ','* ','firm, ','bool ','isNand )',' {\n',
        '  u32 ','argc;\n',
        '  char ','* ','argv[2];\n',
        '  struct ','fb ','fbs[2] ','= ','{\n',
        '    {\n'
    )

def test_code__multiple_empty_line__head_spacing(tmp_path):
    # given
    raw_code =('  } else argc = 1;\n'
             + '\n'
             + '\n'
             + '  launchFirm( firm, argc, argv );\n'
             + '}\n')
    tmp_srcpath = tmp_path/'Formatted_A'/'A'/'EoHo.h' 
    tmp_mappath = tmp_path/'Token_A'/'A'/'EoHo.hmap' 

    fu.write_text(tmp_srcpath, raw_code)
    fu.write_text(
        tmp_mappath, 
        '3 5 10 15 17 \n'
      + '\n'
      + '\n'
      + '3 15 21 27 \n'
      + '1 \n')

    # when
    code = data.code('A', 0, str(tmp_srcpath))

    # then
    assert code.raw == raw_code
    assert code.tokens == (
        '  } ','else ','argc ','= ','1;\n\n\n',


        '  launchFirm( ','firm, ','argc, ','argv );\n',
        '}\n'
    )

def test_code__begin_with_empty_lines__then_no_token_for_starting_empty_line(tmp_path):
    # NOTE: difference of prev case is '\n' in first line
    # given
    raw_code =('\n\n\n'
             + '  } else argc = 1;\n'
             + '\n'
             + '\n'
             + '  launchFirm( firm, argc, argv );\n'
             + '}\n')
    tmp_srcpath = tmp_path/'Formatted_A'/'A'/'EoHo.h' 
    tmp_mappath = tmp_path/'Token_A'/'A'/'EoHo.hmap' 

    fu.write_text(tmp_srcpath, raw_code)
    fu.write_text(
        tmp_mappath, 
        '\n\n\n'
      + '3 5 10 15 17 \n'
      + '\n'
      + '\n'
      + '3 15 21 27 \n'
      + '1 \n')

    # when
    code = data.code('A', 0, str(tmp_srcpath))

    # then
    assert code.raw == raw_code
    print(code.tokens)
    print((
        '  } ','else ','argc ','= ','1;\n\n\n',


        '  launchFirm( ','firm, ','argc, ','argv );\n'
        '}\n'
    ))
    assert code.tokens == (
        '  } ','else ','argc ','= ','1;\n\n\n',


        '  launchFirm( ','firm, ','argc, ','argv );\n',
        '}\n'
    )
