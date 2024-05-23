import yaml


def read_section(section, config_file='config.yaml'):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    # Access the subsections
    try:
        irrelevant_domains = config[section]['irrelevant_subdomains']
        metadata_keep = config[section]['metadata_keep']
        checker_functions = config[section]['checker_functions']

        return irrelevant_domains, metadata_keep, checker_functions
    except KeyError as e:
        raise KeyError("Section not found in config file.") from e
