import re
from bs4 import BeautifulSoup as BS


LAST_TEN_YEARS = r'201[4-9]|202[0-4]'
UNTIL_APRIL_2024 = r'Januar|Februar|März|April'


def spektrum_last_ten_years(data):
    html = data['html_content']
    soup = BS(html, 'lxml')

    date = soup.find('span', id='last_updated')
    if date:
        date = date.get_text().strip()
    else:
        return False

    if re.search(LAST_TEN_YEARS, date):
        if '2024' in date:
            if not re.search(UNTIL_APRIL_2024, date):
                return False
        return True

    return False


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
