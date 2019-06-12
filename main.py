from pathlib import Path
import futils as fu
from hyperpython import h, h1, h2, p, a, meta, link, div, br
import funcy as F

#-----------------------------------------------------------------
from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

src1str = Path('./test/fixture/src1.cpp').read_text()
src2str = Path('./test/fixture/src2.cpp').read_text()
src1 = highlight(src1str, CppLexer(), HtmlFormatter(linenos='table'))
src2 = highlight(src2str, CppLexer(), HtmlFormatter(linenos='table'))

highlight_css = 'css/highlight.css'
fu.write_text(
    highlight_css,
    HtmlFormatter().get_style_defs('.highlight'),
)

table = h('table', children=[
    h('tr')[ h('th')['table'], h('th')['tab'], h('th')['score'],],
    h('tr')[ h('td')['src1'], h('td')['src2'], h('td')[3],],
    h('tr')[ h('td')['src1'], h('td')['src3'], h('td')[3],],
    h('tr')[ h('td')['src1'], h('td')['src4'], h('td')[3],],
    [ h('tr')[ h('td')[1], h('td')[2], h('td')[312],] ] * 100,
])
print(table)

#-----------------------------------------------------------------
def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html')[
        h('head')[head_tags], 
        h('body')[body_tags]
    ]
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr
    #return F.tap('<!DOCTYPE html>\n' + retstr)

fu.write_text('index.html', document_str([], [
    h1('index (start) page'),
    a(href='overview.html')['goto overview'],
]))

#-----------------------------------------------------------------
fu.write_text('overview.html', document_str([], [
    h1('overview page'),
    a(href='compare1.html')['goto compare1'],
    a(href='compare2bi.html')['goto compare2bi'],
]))

#-----------------------------------------------------------------
fu.write_text('compare1.html', 
    document_str(
    [
        meta(name="viewport", content="width=device-width, initial-scale=1"),
        link(rel="stylesheet", href="css/viz1.css"),
        link(rel="stylesheet", href=highlight_css)
    ], 
    [
        div(class_='split left')[
            div(class_='centered')[
                '{source1}',
            ]
        ],
        div(class_='center')[
            div('{source2}')
        ],
        div(class_='split right')[
            table
            #p(children=['right', br()]*100)
        ],
    ]
    ).format_map(dict(source1=src1, source2=src2))
)

#-----------------------------------------------------------------
fu.write_text('compare2bi.html', document_str([], [
    h1('compare2bi page'),
    a(href='matching.html')['goto matching'],
]))

#-----------------------------------------------------------------
fu.write_text('matching.html', document_str([], [
    h1('matching'),
]))
