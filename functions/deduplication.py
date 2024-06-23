import os
import json
import sys
from tqdm import tqdm
from LaBroDoodle.LaBroDoodle import corpusdirs
from . import utils


def markdown_duplicate_elements(
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

    for text in tqdm(
        corpus,
        total=len(corpus),
        desc='Processing text'
    ):
        for para in text.split('\n\n'):
            para = para.strip()
            if len(para) == 0 or para.startswith('#'):
                continue
            para = utils.markdown_to_text(para)
            duplicate_elements[para] = duplicate_elements.get(para, 0) + 1

    return duplicate_elements


def deduplicate_mdtext(
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


def dir_deduplicate_mdtext(
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

        deduped_text = deduplicate_mdtext(
            text,
            duplicate_elements,
            criteria_checker
        )

        if deduped_text is None:
            deduped_text = ''

        data['deduped_text'] = deduped_text

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
