import shutil
import difflib
from pathlib import Path
from collections import namedtuple
import re

import funcy as F
import file_utils as fu
import fp
import main

# Create viz outputs
Args = namedtuple(
    'Args', 
    'input_zip output_directory absolute_score_threshold relative_score_threshold')

try:
    shutil.rmtree('./fixture/0.2.0')
except FileNotFoundError as e:
    print(e)
try:
    shutil.rmtree('./UNZIPPED/')
except FileNotFoundError as e:
    print(e)

for viz_in,viz_out in [
    ('./fixture/answers/mvm/164.125.34.91_2019-07-31-15-56-26.zip', 
    './fixture/0.2.0/mvm'),
    ('./fixture/answers/arm/164.125.34.91_2019-07-31-15-47-54.zip',
    './fixture/0.2.0/arm'),
    ('./fixture/answers/mvs/164.125.34.91_2019-07-31-15-58-01.zip',
    './fixture/0.2.0/mvs')]:
    main.main(Args(
        input_zip=str(viz_in),
        output_directory=str(viz_out),
        absolute_score_threshold=100,
        relative_score_threshold=0.5
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

print('mvm eq?',  (txt_lines_list('./fixture/answers/mvm/out/') 
                == txt_lines_list('./fixture/0.2.0/mvm/')))
print('arm eq?',  (txt_lines_list('./fixture/answers/arm/out/') 
                == txt_lines_list('./fixture/0.2.0/arm/')))
print('mvs eq?',  (txt_lines_list('./fixture/answers/mvs/out/') 
                == txt_lines_list('./fixture/0.2.0/mvs/')))
