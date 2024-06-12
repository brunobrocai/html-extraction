import os
import json
import re
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
from LaBroDoodle import corpusdirs
from . import utils


def json_xml_elements_retrieval(filepath, retrieval_func):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    xml = retrieval_func(data)
    soup = BS(xml, 'lxml-xml')
    element_list = [
        (element.name, element.get_text(separator=' ', strip=True))
        for element in soup.find_all()
    ]
    return element_list


def markdown_deduplication(
    filelist,
    md_getter
):
    duplicate_elements = {}

    corpus = []
    for file in tqdm(
        filelist,
        total=len(filelist),
        desc='Retrieving text from files'
    ):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                corpus.append(md_getter(data))
        except Exception as e:
            print(f'Error in file {file}: {e}')

    for text in corpus:
        for para in text.split('\n\n'):
            para = para.strip()
            if len(para) == 0 or para.startswith('#'):
                continue
            para = utils.markdown_to_text(para)
            duplicate_elements[para] = duplicate_elements.get(para, 0) + 1

    return duplicate_elements


def get_duplicate_elements(
    filelist,
    html_retriever,
):

    seen_elements = set()
    duplicate_elements = {}

    corpus = []
    for file in tqdm(
        filelist,
        total=len(filelist),
        desc='Retrieving text from files'
    ):
        try:
            corpus.extend(json_xml_elements_retrieval(file, html_retriever))
        except Exception as e:
            print(f'Error in file {file}: {e}')

    for element in tqdm(
        corpus,
        total=len(corpus),
        desc='Checking for duplicate elements'
    ):

        if element in seen_elements:
            duplicate_elements[element] = duplicate_elements.get(
                element, 1
            ) + 1
        else:
            seen_elements.add(element)

    print(f'Inspected elements: {len(seen_elements)}')
    print(f'...out of which {len(duplicate_elements)} are duplicates.')

    return duplicate_elements


def deduplicate_text(
    xml,
    duplicate_elements,
    criteria_checker
):
    soup = BS(xml, 'lxml-xml')

    uniq_elements = []
    for element in soup.find_all():

        if element.find_all():
            continue

        try:
            element_tuple = (element.name, element.get_text(separator=' ', strip=True))
            if criteria_checker(
                element_tuple,
                duplicate_elements[element_tuple]
            ):
                continue
        except KeyError:
            pass

        uniq_elements.append(element)

    uniq_text = [
        elem.get_text(separator=' ', strip=True)
        for elem in uniq_elements
    ]
    rawtext = "\n\n".join([t for t in uniq_text if t is not None])
    rawtext = re.sub(r"\n[ \t]*\n([ \t]*\n)+", "\n\n", rawtext)

    return rawtext


def deduplicate_text_md(
    text,
    duplicate_elements,
    criteria_checker
):
    text = text.strip()
    paragraphs = text.split('\n\n')

    uniq_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if len(para) == 0 or para.startswith('#'):
            uniq_paragraphs.append(para)
            continue

        try:
            if criteria_checker(para, duplicate_elements[para]):
                continue
        except KeyError:
            pass

        uniq_paragraphs.append(para)

    return '\n\n'.join(uniq_paragraphs)


def dir_deduped_text_md(
    src,
    duplicate_elements,
    criteria_checker
):

    corpusfiles = corpusdirs.listdir_filetype(src, '.json', absolute=False)

    for file in tqdm(corpusfiles):
        filepath = os.path.join(src, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        text = data['text']

        deduped_text = deduplicate_text_md(
            text,
            duplicate_elements,
            criteria_checker
        )

        if deduped_text is None:
            deduped_text = ''

        data['deduped_text'] = deduped_text

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def dir_deduped_text(
    src,
    duplicate_elements,
    criteria_checker
):

    corpusfiles = corpusdirs.listdir_filetype(src, '.json', absolute=False)

    for file in tqdm(corpusfiles):
        filepath = os.path.join(src, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        deduped_text = deduplicate_text(
            data['text'],
            duplicate_elements,
            criteria_checker
        )

        if deduped_text is None:
            deduped_text = ''

        data['deduped_text'] = deduped_text

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def duplicate_elements_file(
    duplicate_elements,
    criteria_checker,
    filepath
):

    duplicate_texts = []
    for element, count in duplicate_elements.items():
        if criteria_checker(element, count):
            duplicate_texts.append(element)

    text = '\n\n'.join(duplicate_texts)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)


def frequent_paragraphs(element_tuple, count):
    name, text = element_tuple

    if name == 'p' and count >= 3:
        if text.count(' ') + count >= 20:
            return True

    return False


def stern_template_text(element_tuple, count):
    name, text = element_tuple

    if count >= 5:
        return True

    return False


def focus_template_text(element_tuple, count):
    name, text = element_tuple

    if name == 'head' and text.count(' ') < 5:
        if text not in {
            'Anzeige',
            'Spannend, aber gerade keine Zeit?',
            'Das könnte Sie auch interessieren:',
            '(Anzeige)',
            'Das finden andere Nutzer spannend:',
            'Corona Schnelltest für zuhause (Anzeige)',
        }:
            return False

    if name == 'p' and text.count(' ') < 3:
        if text not in {
            'Auch interessant:',
            'Surftipps:',
            '© glomex',
            'Mehr zum Thema:',
            'Lesen Sie auch:',
            'Zum FOCUS Magazin'
        }:
            return False

    if count >= 5:
        return True

    return False


# def join_galleries(directory):
#     json_files = corpusdirs.listdir_filetype(directory, '.json', absolute=True)

#     url_dict = {}

#     for file in tqdm(json_files, desc='Reading urls'):
#         with open(file, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         url_dict[data['crawling_data']['url']] = file

#     joined_galleries = {}

#     for url in url_dict:
#         if re.search('template=gallery', url):
#             continue

#         if re.search(r'_[0-9]{4,}-[0-9]{4,}\.html', url):
#             base_url = re.sub(r'_[0-9]{4,}(-[0-9]{4,})\.html', r'\1.html', url)
#             joined_galleries[base_url] = joined_galleries.get(base_url, [])
#             joined_galleries[base_url].append(url)

#     for base_url, gallery in tqdm(
#         joined_galleries.items(), desc='Joining galleries'
#     ):

#         base_file = url_dict[base_url]
#         with open(base_file, 'r', encoding='utf-8') as f:
#             base_data = json.load(f)

#         expanding_html = base_data['simple_html']

#         for url in gallery:
#             filepath = url_dict[url]
#             with open(filepath, 'r', encoding='utf-8') as f:
#                 data = json.load(f)

#             expanding_html = expanding_html + '\n' + data['simple_html']

#         print(expanding_html)
#         break

#         # base_file = os.path.join(directory, url_dict[base_article])
#         # with open(base_file, 'r', encoding='utf-8') as f:
#         #     base_data = json.load(f)

#         # base_data['gallery'] = gallery_data

#         # with open(base_file, 'w', encoding='utf-8') as f:
#         #     json.dump(base_data, f, ensure_ascii=False, indent=4)
