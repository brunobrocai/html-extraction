import re
from . import meta_funcs


class MetaRetriever():
    """Class for extracting metadata BeautifulSoup objects."""

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        if value is not None:
            try:
                iter(value)
            except TypeError as excep:
                message = "Labels must be an iterable."
                raise ValueError(message) from excep
        self._labels = value

    @property
    def kywd_extraction_func(self):
        return self._kywd_extraction_func

    @kywd_extraction_func.setter
    def kywd_extraction_func(self, value):
        self._kywd_extraction_func = value

    @property
    def other_info_funcs(self):
        return self._other_info_funcs

    @other_info_funcs.setter
    def other_info_funcs(self, value):
        try:
            iter(value)
        except TypeError as excep:
            raise ValueError("Other info functions must be an iterable.") from excep
        self._other_info_funcs = value

    def __init__(
        self, metadata_labels_keep=None,
        kywd_extraction_func='keyword_getter_basic',
        other_info_funcs=('get_h1')
    ):
        self._labels = metadata_labels_keep
        self._kywd_extraction_func = kywd_extraction_func
        self._other_info_funcs = other_info_funcs

    def fill_meta_dict(self, soup):
        meta_data = soup.find_all("meta")
        meta_dict = {}
        for datum in meta_data:
            name = datum.get("name")
            if name:
                meta_dict[name] = datum.get("content")
            else:
                proprty = datum.get("property")
                if proprty:
                    meta_dict[proprty] = datum.get("content")

        meta_dict = {
            k: v for k, v in meta_dict.items()
            if k in self.labels
        }

        return meta_dict

    def fill_other_info(self, soup):
        other_info = {}
        for function in self.other_info_funcs:
            function = getattr(meta_funcs, function)
            key, value = function(soup)
            other_info[key] = value

        return other_info

    def full_pipeline(self, soup):
        meta_dict = self.fill_meta_dict(soup)
        other_info = self.fill_other_info(soup)
        if self.kywd_extraction_func:
            kywd_extraction_func = getattr(
                meta_funcs, self.kywd_extraction_func
            )
            keywords = kywd_extraction_func(soup)
            meta_dict["keywords"] = keywords
        meta_dict.update(other_info)
        return meta_dict


def keywd_gttr_factory(separator_pattern=r",|;"):
    def keyword_getter(soup):
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

    return keyword_getter


def get_figures(soup, main_body_element=None):
    if not main_body_element:
        figures = soup.find_all("figure")
    else:
        main_body = soup.find(main_body_element)
        figures = main_body.find_all("figure")
    figure_info = []

    for figure in figures:
        fig_dict = {}
        figcaption = figure.find("figcaption")
        if figcaption:
            fig_dict["caption"] = figcaption.get_text(
                separator="\n",
                strip=True
            )
        else:
            fig_dict["caption"] = None
        image = figure.find("img")
        fig_dict["src"] = image["src"]
        fig_dict["alt"] = image["alt"]
        figure_info.append(fig_dict)

    return figure_info


def get_h1(soup):
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return None


def keyword_getter_basic(soup):
    return keywd_gttr_factory()(soup)


def meta_df_to_dict(df):

    meta_dict = dict(zip(df["label"], df["content"]))
    return meta_dict


def extract_metadata_from_article(
    soup, labels, keywd_getter=keyword_getter_basic, h1_getter=get_h1
):
    # Extracts metadata from the html content
    # Return a pandas dataframe with the metadata
    meta_data = soup.find_all("meta")

    def create_meta_dict(meta_data):
        meta_dict = {}
        for datum in meta_data:
            name = datum.get("name")
            if name:
                meta_dict[name] = datum.get("content")
            else:
                proprty = datum.get("property")
                if proprty:
                    meta_dict[proprty] = datum.get("content")
        return meta_dict

    meta_dict_full = create_meta_dict(meta_data)

    meta_dict = {k: v for k, v in meta_dict_full.items() if k in labels}

    # Get the title of the article
    title = h1_getter(soup)
    keywords = keywd_getter(soup)

    if title:
        meta_dict["title"] = title
    if keywords:
        meta_dict["keywords"] = keywords

    return meta_dict


if __name__ == "__main__":
    from bs4 import BeautifulSoup as BS

    with open("test_files/spektrum_test1.html", "r", encoding="utf-8") as f:
        html_str = f.read()

    soup = BS(html_str, "lxml")
    print(get_figures(soup, 'article'))
