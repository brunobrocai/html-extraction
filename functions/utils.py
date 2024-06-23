import re
import os
import markdown
from bs4 import BeautifulSoup as BS


def markdown_to_text(text):
    """ Converts a markdown string to plaintext.
    Credit: 'lorey' on GitHub,
    https://gist.github.com/lorey/eb15a7f3338f959a78cc3661fbc255fe"""

    text = re.sub(r'\*\*(.*)\*\*', r' \1 ', text)
    text = re.sub(r'\*\b(.*)\b\*', r' \1 ', text)
    text = re.sub(r'  +', ' ', text)
    lines = text.split('\n')

    new_lines = []
    for line in lines:
        if line.strip().startswith('#'):
            new_lines.extend(['', line, ''])
        else:
            new_lines.append(line)

    text = '\n'.join(new_lines)

    html = markdown.markdown(text)

    # extract text
    soup = BS(html, "lxml")
    text = '\n'.join(soup.findAll(text=True))

    lines = text.split('\n')
    text = '\n'.join([line.strip() for line in lines])

    return text


def rename_files_with_padded_index(directory):
    # Get list of files in the directory
    files = [
        file for file in os.listdir(directory)
        if not file.endswith('.py')
        and os.path.isfile(os.path.join(directory, file))
    ]

    # Calculate the total number of digits needed for the highest index
    num_files = len(files)
    num_digits = len(str(num_files))

    # Iterate over each file and rename it with a zero-padded index
    for index, filename in enumerate(files):
        # Construct zero-padded index
        padded_index = str(index + 1).zfill(num_digits)

        # Construct new filename with padded index
        new_filename = f"{padded_index}.json"

        # Rename the file
        os.rename(
            os.path.join(directory, filename),
            os.path.join(directory, new_filename)
        )
