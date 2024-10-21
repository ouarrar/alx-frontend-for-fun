#!/usr/bin/python3
"""
Converts a markdown file to HTML with specific transformations:
- Bold text (**bold**)
- Emphasis text (__emphasized__)
- Converts text within '[[' and ']]' to MD5
- Removes 'C' and 'c' from text within '((' and '))'
"""
import hashlib
import os
import sys


def bold_emphasis(line, markdown):
    """
    Transforms specified text to bold or emphasized HTML tags.

    Args:
        line (str): The line of text to modify.
        markdown (str): Either '**' for bold or '__' for emphasis.

    Returns:
        str: The modified text with HTML tags.
    """
    parts = line.split(markdown)
    tag = 'b' if markdown == '**' else 'em'

    for index in range(1, len(parts), 2):
        parts[index] = f'<{tag}>{parts[index]}</{tag}>'

    modified_line = ''.join(parts)

    return modified_line


def text_to_md5(text):
    """
    Converts text within '[[' and ']]' to its MD5 hash.

    Args:
        text (str): The line of text to process.

    Returns:
        str: The modified line with MD5 hash.
    """
    if '[[' in text and ']]' in text:
        opening = text.find('[[')
        closing = text.find(']]')
        to_md5 = text[opening + 2:closing]

        hash_text = hashlib.md5(to_md5.encode()).hexdigest()
        merged_text = f'{text[:opening]}{hash_text}{text[closing + 2 :]}'

        return merged_text
    else:
        return text


def remove_c(text):
    """
    Removes all instances of 'C' and 'c' from text within '((' and '))'.

    Args:
        text (str): The line of text to modify.

    Returns:
        str: The modified line with 'C' and 'c' removed.
    """
    if '((' in text and '))' in text:
        opening = text.find('((')
        closing = text.find('))')

        to_replace = text[opening + 2:closing]
        replaced = to_replace.replace('C', '').replace('c', '')
        merged_text = f'{text[:opening]}{replaced}{text[closing + 2:]}'

        return merged_text
    else:
        return text


def process_line(line):
    """
    Processes the line to apply markdown transformations: bold, emphasis,
    MD5 conversion, and 'C' removal.

    Args:
        line (str): The input line to process.

    Returns:
        str: The fully processed line with transformations applied.
    """
    bold_text = bold_emphasis(line, '**')
    em_text = bold_emphasis(bold_text, '__')
    hash_text = text_to_md5(em_text)
    no_c_text = remove_c(hash_text)

    return no_c_text


if __name__ == "__main__":

    args = sys.argv[1:]

    if len(args) < 2:
        err = "Usage: ./markdown2html.py README.md README.html"
        print(err, file=sys.stderr)
        exit(1)

    markdown_file = args[0]
    html_file = args[1]

    if not os.path.isfile(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        exit(1)

    with open(markdown_file) as mdfile:
        with open(html_file, 'a') as htmlfile:
            # Flag to track opening and closing of list items
            list_started = False

            # Flag to track opening and closing of paragraph
            paragraph_started = False

            # Holds either <ol> or <ul>
            list_type = ''

            for line in mdfile:
                # Heading section
                if line.startswith('#'):
                    # If there is an open list, close it first
                    if list_started:
                        htmlfile.write(f'</{list_type}>\n')
                        list_started = False

                    # If there is an open paragraph, close it first
                    if paragraph_started:
                        htmlfile.write('</p>\n')
                        paragraph_started = False

                    line = line.strip()
                    count = 0

                    while count < len(line) and line[count] == '#':
                        count += 1

                    if line[count] == ' ':
                        text = line[count + 1:]
                        head_text = process_line(text)

                        htmlfile.write(f'<h{count}>{head_text}</h{count}>\n')

                # Listing section
                elif line.startswith('- ') or line.startswith('* '):
                    # If there is an open paragraph, close it first
                    if paragraph_started:
                        htmlfile.write('</p>\n')
                        paragraph_started = False

                    line = line.strip()

                    if line.startswith('- '):
                        list_type = 'ul'
                    elif line.startswith('* '):
                        list_type = 'ol'

                    text = line[2:]

                    if not list_started:
                        htmlfile.write(f'<{list_type}>\n')
                        list_started = True

                    list_text = process_line(text)

                    htmlfile.write(f'<li>{list_text}</li>\n')

                # Paragraph section
                elif (line and line[0].isalpha()) or line.isspace()\
                    or line.startswith('**') or line.startswith('__')\
                    or line.startswith('((') or line.startswith('[['):
                    # If there is an open list, close it first
                    if list_started:
                        htmlfile.write(f'</{list_type}>\n')
                        list_started = False

                    if not paragraph_started:
                        if not line.isspace():
                            paragraph_started = True
                            htmlfile.write('<p>\n')
                    elif paragraph_started:
                        if line.isspace():
                            htmlfile.write('\n</p>\n')
                            paragraph_started = False
                        else:
                            htmlfile.write('\n<br/>\n')

                    line = line.strip()
                    paragraph_text = process_line(line)

                    htmlfile.write(paragraph_text)

            if list_started:
                htmlfile.write(f'</{list_type}>\n')

            if paragraph_started:
                htmlfile.write('\n</p>\n')