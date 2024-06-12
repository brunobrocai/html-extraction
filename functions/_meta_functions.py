import re


# +++++Keyword Getters+++++

def keyword_getter_basic(soup):
    separator_pattern = r",|;"
    keywords = soup.find("meta", attrs={"name": "keywords"})
    if keywords:
        keyword_list = re.split(
            separator_pattern, keywords["content"]
        )
        keyword_list = [
            keyword.strip() for keyword in keyword_list
        ]
        keyword_list = [
            keyword for keyword in keyword_list if len(keyword) > 0
        ]
        return keyword_list
    return None


def no_keywords():
    return []


# +++++Other Info Getters+++++

def get_h1(soup):
    h1 = soup.find("h1")
    if h1:
        return 'h1', h1.get_text(strip=True)
    return 'h1', None
