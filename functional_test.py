import shutil
from collections import namedtuple

import main

def test_no_matches_but_ok():
    Args = namedtuple(
        'Args', 
        'input_zip output_directory absolute_score_threshold relative_score_threshold')
    main.main(Args(
        input_zip=str('fixture/no-match-case/164.125.34.91_2019-08-21-14-27-04.zip'),
        output_directory=str('tmp'),
        absolute_score_threshold=100,
        relative_score_threshold=0.5
    ))

    try:
        shutil.rmtree('tmp')
    except FileNotFoundError as e:
        print(e)

    print('No crash, then ok. Check buttons in index.html later')

test_no_matches_but_ok()
