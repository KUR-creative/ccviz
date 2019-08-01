import shutil
import difflib
from pathlib import Path
from collections import namedtuple

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
    ('./fixture/0.1.0/mvm/164.125.34.91_2019-07-31-15-56-26.zip', 
    './fixture/0.2.0/mvm'),
    ('./fixture/0.1.0/arm/164.125.34.91_2019-07-31-15-47-54.zip',
    './fixture/0.2.0/arm'),
    ('./fixture/0.1.0/mvs/164.125.34.91_2019-07-31-15-58-01.zip',
    './fixture/0.2.0/mvs')]:
    main.main(Args(
        input_zip=str(viz_in),
        output_directory=str(viz_out),
        absolute_score_threshold=100,
        relative_score_threshold=0.5
    ))
