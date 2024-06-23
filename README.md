# HTML-conversion-basic

## Description
Code to extract text and metadata from html webpages. Designed to be easily and quickly adapted to different websites.

## Requirements
You need the following python packages:
- bs4
- pyyaml
- tqdm
- trafilatura
- matplotlib
- markdown
- lxml

You can install them with:
```bash
pip install bs4 pyyaml tqdm trafilatura matplotlib markdown lxml
```

You also need to install the git submodule LaBroDoodle:
```bash
pip install LaBroDoodle
```

## Usage
1. Run the 'explore' notebook to better understand the corpus and the structure of the html pages and the urls. Decide what information is important to you.
2. Configure the yaml config file with info about the website and the desired output.
   1. irrelevant_subdomains: list of regex patterns that, if they appear in a url, the page will be ignored.
   2. metadata_keep: list of metadata keys that will be kept.
   3. If necessary, look at the html structure and configure personal functions that help eliminate irrelevant pages, e.g. those locked behind a paywall.
3. Run the 'extract' notebook to extract the text and metadata from the html pages.
4. Optional, depending on the website: join pages that were separated into multiple html files.
5. Optional, but recommended: Run the 'deduplicate' notebook to remove duplicate (template) text
