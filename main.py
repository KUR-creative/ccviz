'''
from yattag import Doc

def main():
    doc, tag, text = Doc().tagtext()

    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('body'):
            with tag('h1'):
                text('Hello world!')

    print(doc.getvalue())

if __name__ == '__main__':
    main()
'''

import futils as fu
from hyperpython import h, h1, a

'''
def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html', children = [
        h('head', children=head_tags),
        h('body', children=body_tags)
    ])
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr

print(document_str(
    [h1('ppap'),
     a(href='https://github.com/ejplatform/hyperpython')['goto','2nd']],
    ['aa']))
    '''

def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html')[
        h('head')[head_tags], 
        h('body')[body_tags]
    ]
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr

print(document_str(
    [], [
        h1('index (start) page'),
        a(href='overview.html')['goto overview'],
    ]))

fu.write_text('index.html', document_str([], [
    h1('index (start) page'),
    a(href='overview.html')['goto overview'],
]))

fu.write_text('overview.html', document_str([], [
    h1('overview page'),
    a(href='compare1.html')['goto compare1'],
    a(href='compare2bi.html')['goto compare2bi'],
]))

fu.write_text('compare1.html', document_str([], [
    h1('compare1 page'),
    a(href='matching.html')['goto matching'],
]))

fu.write_text('compare2bi.html', document_str([], [
    h1('compare2bi page'),
    a(href='matching.html')['goto matching'],
]))

fu.write_text('matching.html', document_str([], [
    h1('matching'),
]))
