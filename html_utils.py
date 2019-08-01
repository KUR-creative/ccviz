import re

import funcy as F
import fp

def emphasized(line, color):
    return '<span style="background-color:{}; width:100%; float:left;">{} </span>'.format(
        color, line
    ) if color else line

def tag_regex(tag_name):
    '''
    TODO: Returned_re.findall(s) makes tuple of list.. This is too bad!!
    '''
    return re.compile(
        '<\s*'+tag_name+'[^>]*>((.|\n|\r|\r\n)*?)<\s*/\s*'+tag_name+'>'
    )

def all_pre(html_str):
    return fp.lmap(F.first, tag_regex('pre').findall(html_str))
