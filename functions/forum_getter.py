def paradisi_entries(soup):
    """
    Get all entries from a paradisi forum thread
    :param soup: BeautifulSoup object
    :return: list of entries
    """

    post_elements = soup.find_all('div', class_='post__content')
    post_infos = soup.find_all('div', class_='post__head-infos')
    post_footers = soup.find_all('div', class_='post__footer')

    posts = []
    for i, entry in enumerate(post_elements):
        info = post_infos[i]
        footer = post_footers[i]
        entry_text = entry.get_text(separator='\n', strip=True)
        entry_likes = footer.find('span', class_='rating__count')
        entry_likes = int(entry_likes.get_text()) if entry_likes else 0
        entry_author = info.find('span', {'itemprop': 'name'}).get_text()
        entry_date = info.find('time', {'itemprop': 'dateCreated'})['datetime']
        entry_is_op = i == 0

        post = {
            'text': entry_text,
            'likes': entry_likes,
            'author': entry_author,
            'date': entry_date,
            'is_op': entry_is_op,
            'is_expert': False
        }
        posts.append(post)

    return posts
