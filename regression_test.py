# map <F8> :wa<CR>:!rm -rf OUT/encode_err/;python ccviz.py TEST_DATA/encode_err/164.125.34.86_2019-10-08-18-47-16.zip -o OUT/encode_err
import shutil
import difflib
from pathlib import Path
from collections import namedtuple
import re

import funcy as F
import file_utils as fu
import fp
import ccviz

# Create viz outputs
Args = namedtuple(
    'Args', 
    'input_zip output_directory absolute_score_threshold relative_score_threshold no_highlight_threshold')

try:
    shutil.rmtree('test_out/')
except FileNotFoundError as e:
    print(e)
try:
    shutil.rmtree('./UNZIPPED/')
except FileNotFoundError as e:
    print(e)


ios = [('fixture/tmp-matching-window/complex/164.125.34.92_2019-09-06-11-55-17.zip',
        'test_out/complex'),
       ('fixture/tmp-matching-window/arm9_11/strong_link/164.125.34.91_2019-09-06-08-44-26.zip',
        'test_out/arm'),]
for viz_in,viz_out in ios:
    ccviz.main(Args(
        input_zip=str(viz_in),
        output_directory=str(viz_out),
        absolute_score_threshold=10,
        relative_score_threshold=0.1,
        no_highlight_threshold=500000
    ))

# https://stackoverflow.com/questions/7543818/regex-javascript-to-match-both-rgb-and-rgba
rgba_regex = re.compile(
    "background-color:rgba?\(((25[0-5]|2[0-4]\d|1\d{1,2}|\d\d?)\s*,\s*?){2}(25[0-5]|2[0-4]\d|1\d{1,2}|\d\d?)\s*,?\s*([01]\.?\d*?)?\);"
)

# Compare outputs and fixture
txt_lines_list = fp.pipe(
    fu.descendants,
    fu.human_sorted,
    fp.map(fu.read_text),
    fp.map(F.partial(re.sub, rgba_regex, '')), # remove random generated color
    fp.lmap(lambda s: s.splitlines()),
)

assert txt_lines_list('./fixture/answers/complex/') \
    == txt_lines_list('./test_out/complex'), 'complex failed!'
assert txt_lines_list('./fixture/answers/arm/') \
    == txt_lines_list('./test_out/arm'), 'arm failed!'
print('test passed!')

