import concurrent.futures
import os
import json
from bs4 import BeautifulSoup as BS
from tqdm import tqdm
from . import article_getter, meta_retrieval, check_relevance, config_parsing, forum_getter


def transform_raw_json(
    sourcefile,
    goaldir,
    relevance_checks,
    metadata_keep,
    extraction_function_keywords={},
    metadata_function=meta_retrieval.extract_metadata_from_article,
):

    with open(sourcefile, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not relevance_checks(data):
        return None

    html_content = data["html_content"]
    if not html_content:
        return None

    soup = BS(html_content, "lxml")
    if not soup:
        return None

    simple_xml, text = article_getter.get_xml_and_text(
        html_content, **extraction_function_keywords)
    if not text:
        return None

    meta_dict = metadata_function(soup, metadata_keep)

    cleaned_data = {
        "url": data["url"],
        "time_crawled": data["time_crawled"],
        "xml": simple_xml,
        "text": text,
    } | meta_dict

    goalpath = os.path.join(goaldir, os.path.basename(sourcefile))

    with open(goalpath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    return None


def extract_files_parallel(
    source_dir,
    goal_dir,
    config_section,
    extraction_function_keywords={},
):
    # Create a ThreadPoolExecutor with the specified number of threads
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=12)
    futures = {}

    relevance_checks = check_relevance.make_relevance_checks(config_section)
    _, metadata_keep, _ = config_parsing.read_section(config_section)

    sourcefiles = [
        os.path.join(source_dir, file)
        for file in os.listdir(source_dir)
        if file.endswith(".json")
    ]

    # Iterate over the raw_corpus and submit the tasks to the executor
    for sourcefile in tqdm(
        sourcefiles, desc="Processing JSON files", unit="file"
    ):
        future = executor.submit(
            transform_raw_json,
            sourcefile,
            goal_dir,
            relevance_checks,
            metadata_keep,
            extraction_function_keywords,
        )
        futures[future] = sourcefile

    # Iterate over the futures as they complete
    for future in tqdm(
        concurrent.futures.as_completed(futures),
        total=len(futures),
        desc="Processing futures",
        unit="future",
    ):
        sourcefile = futures[future]
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred while processing {sourcefile}: {e}")

    # Print the number of processed files
    print(f"Processed {len(futures)} files.")


def extract_files_sequential(
    source_dir,
    goal_dir,
    config_section,
    extraction_function_keywords={},
):

    relevance_checks = check_relevance.make_relevance_checks(config_section)
    _, metadata_keep, _ = config_parsing.read_section(config_section)

    sourcefiles = [
        os.path.join(source_dir, file)
        for file in os.listdir(source_dir)
        if file.endswith(".json")
    ]

    for sourcefile in tqdm(
        sourcefiles, desc="Processing JSON files", unit="file"
    ):
        transform_raw_json(
            sourcefile,
            goal_dir,
            relevance_checks,
            metadata_keep,
            extraction_function_keywords,
        )

    print(f"Processed {len(sourcefiles)} files.")


def transform_forum_json(
    sourcefile,
    goaldir,
    relevance_checks,
    metadata_keep,
    extraction_function_keywords={},
    metadata_function=meta_retrieval.extract_metadata_from_article,
):
    with open(sourcefile, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not relevance_checks(data):
        return None

    html_content = data["html_content"]
    if not html_content:
        return None

    soup = BS(html_content, "lxml")
    if not soup:
        return None

    discussion = forum_getter.paradisi_entries(soup)
    if not discussion:
        return None

    text = "\n\n\n".join([entry["text"] for entry in discussion])

    meta_dict = metadata_function(soup, metadata_keep)

    cleaned_data = {
        "url": data["url"],
        "time_crawled": data["time_crawled"],
        "discussion": discussion,
        "text": text,
    } | meta_dict

    goalpath = os.path.join(goaldir, os.path.basename(sourcefile))

    with open(goalpath, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    return None


def extract_forum_parallel(
    source_dir,
    goal_dir,
    config_section,
    extraction_function_keywords={},
):
    # Create a ThreadPoolExecutor with the specified number of threads
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=12)
    futures = {}

    relevance_checks = check_relevance.make_relevance_checks(config_section)
    _, metadata_keep, _ = config_parsing.read_section(config_section)

    sourcefiles = [
        os.path.join(source_dir, file)
        for file in os.listdir(source_dir)
        if file.endswith(".json")
    ]

    # Iterate over the raw_corpus and submit the tasks to the executor
    for sourcefile in tqdm(
        sourcefiles, desc="Processing JSON files", unit="file"
    ):
        future = executor.submit(
            transform_forum_json,
            sourcefile,
            goal_dir,
            relevance_checks,
            metadata_keep,
            extraction_function_keywords,
        )
        futures[future] = sourcefile

    # Iterate over the futures as they complete
    for future in tqdm(
        concurrent.futures.as_completed(futures),
        total=len(futures),
        desc="Processing futures",
        unit="future",
    ):
        sourcefile = futures[future]
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred while processing {sourcefile}: {e}")

    # Print the number of processed files
    print(f"Processed {len(futures)} files.")
