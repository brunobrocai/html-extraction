from bs4 import BeautifulSoup as BS


def stern_is_free(data):
    soup = BS(data['html'], 'lxml')

    if soup.find(
        'div', {'class': 'title__logo title__logo--str_plus'}
    ):
        return False
    return True
