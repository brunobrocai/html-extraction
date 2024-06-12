import re
from . import config_parsing, checker_functions


def is_relevant(url, irrel_pattern=None, irrel_pattern_list=None):
    """Check if a url is relevant based on a pattern."""
    if irrel_pattern_list:
        for pattern in irrel_pattern_list:
            if re.search(pattern, url):
                return False
        return True
    if irrel_pattern:
        return not re.search(irrel_pattern, url)
    raise AttributeError("No pattern or pattern list provided.")


def make_relevance_checks(config_section):
    irrel_domains, _, checker_funcs = config_parsing.read_section(
        config_section
    )

    def relevance_checks(data):
        if checker_funcs is not None:
            for function in checker_funcs:
                function = getattr(checker_functions, function)
                if not function(data):
                    return False
        if not is_relevant(data["url"], irrel_pattern_list=irrel_domains):
            return False
        return True

    return relevance_checks
