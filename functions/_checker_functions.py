from bs4 import BeautifulSoup as BS


def stern_is_free(data):
    soup = BS(data['html'], 'lxml')

    if soup.find(
        'div', {'class': 'title__logo title__logo--str_plus'}
    ):
        return False
    return True


def paradisi_forum_is_health(data):

    paradisi_health = {
        'Gesundheit', 'Medizin'
    }

    soup = BS(data['html_content'], 'lxml')
    tag_section = soup.find('section', {'class': 'tags'})

    if tag_section is None:
        return False

    for element in tag_section.find_all('a'):
        if element.text in paradisi_health:
            return True

    return False
