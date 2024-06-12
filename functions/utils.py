import re
import markdown
from bs4 import BeautifulSoup as BS


def markdown_to_text(text):
    """ Converts a markdown string to plaintext.
    Credit: 'lorey' on GitHub,
    https://gist.github.com/lorey/eb15a7f3338f959a78cc3661fbc255fe"""

    text = re.sub(r'\*\*(.*)\*\*', r' \1 ', text)
    text = re.sub(r'  +', ' ', text)
    lines = text.split('\n')

    new_lines = []
    for line in lines:
        if line.strip().startswith('#'):
            new_lines.extend(['', line, ''])
        else:
            new_lines.append(line)

    text = '\n'.join(new_lines)

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown.markdown(text)

    # extract text
    soup = BS(html, "html.parser")
    text = '\n'.join(soup.findAll(text=True))

    lines = text.split('\n')
    text = '\n'.join([line.strip() for line in lines])

    return text


def cleaner_markdown():
    print()
