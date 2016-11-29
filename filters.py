import functools
import re

bold = functools.partial(
    re.compile(r'(.*?)\*(.*?)\*(.*?)').sub,
    r'\1<span style="font-weight:bold;">\2</span>\3'
)

italic = functools.partial(
    re.compile(r'(.*?)/(?!>)(.*?)/(.*?)').sub,
    r'\1<span style="font-style:italic;">\2</span>\3'
)

underlined = functools.partial(
    re.compile(r'(.*?)_(.*?)_(.*?)').sub,
    r'\1<span style="text-decoration:underline">\2</span>\3'
)

verbatim = functools.partial(
    re.compile(r'(.*?)=(.*?)=(.*?)').sub,
    r'\1<pre>\2</pre>\3'
)

code = functools.partial(
    re.compile(r'(.*?)~(.*?)~(.*?)').sub,
    r'\1<span style="font-family:monospace;">\2</span>\3'
)

strike_through = functools.partial(
    re.compile(r'(.*?)+(.*?)+(.*?)').sub,
    r'\1<span style="text-decoration: overline;">\2</span>\3'
)

stylers = [
    bold, italic, underlined, code, strike_through
]

def org(org):
    for styler in stylers:
        org = styler(org)
    return org
