from hyperpython import h
def document_str(head_tags,body_tags,is_pretty=True):
    doc = h('html')[
        h('head')[head_tags], 
        h('body')[body_tags]
    ]
    retstr = str(doc.pretty() if is_pretty else doc)
    return '<!DOCTYPE html>\n' + retstr
