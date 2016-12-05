import functools
import html
import re

import config as cfg

def headline(s):
    m = re.match(r'^(?P<level>\*+)\s+(?P<title>.+?)\s*$', s)
    if m:
        return '<h{level}>{title}</h{level}>'.format(
            level=len(m.groupdict()['level'])+1,
            title=m.groupdict()['title']
        )
    else:
        return s

bold = functools.partial(
    re.compile(r'(.*?)\*([^*]+?)\*(.*?)').sub,
    r'\1<span style="font-weight:bold;">\2</span>\3'
)

italic = functools.partial(
    re.compile(r'(.*?)/(?!>)(.*?)/(.*?)').sub,
    r'\1<span style="font-style:italic;">\2</span>\3'
)

underlined = functools.partial(
    re.compile(r'(.*?)_(.*?)_(.*?)').sub,
    r'\1<span style="text-decoration:underline;">\2</span>\3'
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
    re.compile(r'(.*?)\+(.*?)\+(.*?)').sub,
    r'\1<span style="text-decoration: line-through;">\2</span>\3'
)

hyperlink_with_description = functools.partial(
    re.compile(r'(?P<before>.*?)\[\[(?P<link>https?://.+?)\]\[(?P<description>).+?\]\](P<after>.*?)').sub,
    r'\g<before><a href="\g<link>">\g<description></a>\g<after>'
)

hyperlink_without_description = functools.partial(
    re.compile(r'(?P<before>.*?)\[\[(?P<link>https?://.+?)\]\](P<after>.*?)').sub,
    r'\g<before><a href="\g<link>">\g<link></a>\g<after>'
)


image = functools.partial(
    re.compile(r'(?P<before>.*?)\[\[(?P<filename>.+?)(?P<c>:)?(?(c)(?P<caption>.+))\]\](?P<w>::)?(?(w)(?P<width>\d+)px|)(?P<after>.*?)').sub,
    r'\g<before><div class="center imagebox"><img src="/{}/\g<filename>" width=\g<width>><br /><span class="caption">\g<caption></span></div>\g<after>'.format(cfg.img_save_path)
)


stylers = [
    bold, italic, underlined, verbatim, code, strike_through,
    headline,
    hyperlink_with_description, hyperlink_without_description,
    image
]

def org(org):
    org = org.split('\n')
    ret = []
    for line in org:
        line = re.sub(r'(.*?)<more>(.*?)', r'\1\2', line)
        for styler in stylers:
            line = styler(line)
        if re.match(r'(.+?)</h[1-6]>$', line):
            ret.append(line)
        else:
            ret.append(line + '<br />')
    return "".join(ret)

def org_esc(org):
    org = org.splitlines()
    ret = []
    for line in org:
        line = re.sub(r'(.*?)<more>(.*?)', r'\1\2', line)
        line = html.escape(line)
        for styler in stylers:
            line = styler(line)
        ret.append(line)
    return "\n".join(ret)

def image_filepath(filename):
    return '/' + cfg.img_save_path + '/' + filename
