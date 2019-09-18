# map <F5> :wa<CR>:!pytest -vv data_test.py<CR>
# map <F7> :wa<CR>:!rm -rf tmp2/;python ccviz.py fixture/tmp-matching-window/ms/164.125.34.91_2019-08-30-12-40-03.zip -o tmp-result/tmp-matching-window/ms<CR>
# map <F8> :wa<CR>:!rm -rf tmp-result/tmp-matching-window/arm9_11; python ccviz.py fixture/tmp-matching-window/arm9_11/strong_link/164.125.34.91_2019-09-06-08-44-26.zip -a 10 -r 0.1 -o tmp-result/tmp-matching-window/arm9_11/strong_link<CR>
import data
import file_utils as fu

def case_for_code(src, xmap):
    return data.tokens(src,xmap)

def test_tokens__no_empty_line__no_head_spacing():
    assert case_for_code(
      # code.x
        '#include "firm.h"\n'
      + '#include "memory.h"\n' 
      + '#include "cache.h"',
      # code.xmap
        '1 10 \n'
      + '1 10 \n'
      + '1 10 \n') \
    == ( # result tokens
        '#include ', '"firm.h"\n',
        '#include ', '"memory.h"\n',
        '#include ', '"cache.h"')

def test_tokens__no_empty_line__head_spacing():
    assert case_for_code(
      # code.x
        'void main( Firm * firm, bool isNand ) {\n'
      + '  u32 argc;\n'
      + '  char * argv[2];\n'
      + '  struct fb fbs[2] = {\n'
      + '    {\n', # TODO: last '\n' have to do not affect result?
      # code.xmap
        '1 12 17 19 25 30 38 \n'
      + '3 7 \n'
      + '3 8 10 \n'
      + '3 10 13 20 22 \n'
      + '5\n') \
    == ( # result tokens
        'void main( ','Firm ','* ','firm, ','bool ','isNand )',' {\n',
        '  u32 ','argc;\n',
        '  char ','* ','argv[2];\n',
        '  struct ','fb ','fbs[2] ','= ','{\n',
        '    {\n')

def test_tokens__multiple_empty_line__head_spacing():
    assert case_for_code(
      # code.x
        '  } else argc = 1;\n'
      + '\n'
      + '\n'
      + '  launchFirm( firm, argc, argv );\n'
      + '}\n',
      # code.xmap
        '3 5 10 15 17 \n'
      + '\n'
      + '\n'
      + '3 15 21 27 \n'
      + '1 \n') \
    == ( # result tokens
        '  } ','else ','argc ','= ','1;\n\n\n',


        '  launchFirm( ','firm, ','argc, ','argv );\n',
        '}\n')

def test_tokens__begin_with_empty_lines__then_no_token_for_starting_empty_line():
    # NOTE: difference between this and prev case is '\n' in first line
    assert case_for_code(
      # code.x
        '\n\n\n'
      + '  } else argc = 1;\n'
      + '\n'
      + '\n'
      + '  launchFirm( firm, argc, argv );\n'
      + '}\n',
        '\n\n\n'
      # code.xmap
      + '3 5 10 15 17 \n'
      + '\n'
      + '\n'
      + '3 15 21 27 \n'
      + '1 \n') \
    == ( # result tokens
        '  } ','else ','argc ','= ','1;\n\n\n',


        '  launchFirm( ','firm, ','argc, ','argv );\n',
        '}\n')
