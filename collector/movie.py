from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import requests
import re
from decimal import Decimal

from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.core.files import File

from shows.models import Movie, Season, Episode

URL = 'https://myshows.me/'


def collect_data(external_id):
    url = URL + f'view/{external_id}/'
    page = requests.get(url)
    html = BeautifulSoup(page.text, "html.parser")
    return html


class ParseInfo:

    @staticmethod
    def movie(external_id):
        try:
            m = Movie.objects.get(external_id=external_id)

        except Movie.DoesNotExist:
            m = Movie()
            html = collect_data(external_id)

            m.external_id = external_id
            try:
                m.first_title = html.find("h1", itemprop='name').text.rstrip()
            except AttributeError:
                m.first_title = None

            try:
                m.second_title = html.find("p", class_='subHeader').text.rstrip()
            except AttributeError:
                m.second_title = None

            info = html.find(class_='clear')

            dates = info.find(class_='flat').text.split(': ')[1].split(' – ')

            try:
                m.start_date = parse(dates[0])
            except ValueError:
                m.start_date = None


            try:
                m.end_date = parse(dates[1]) if dates[1] != '…' or '---' else None
            except ValueError:
                m.end_date = None

            clear_data = html.find(class_='clear')
            m.country = clear_data.find(string='Страна:').parent.parent.find('a').text or None
            try:
                m.imdb = clear_data.find(string='Рейтинг IMDB:').parent.parent.find(target='_blank').text
            except AttributeError:
                m.imdb = Decimal(0.0)
            try:
                m.kp = clear_data.find(string='Рейтинг Кинопоиска:').parent.parent.find(target='_blank').text
            except AttributeError:
                m.kp = Decimal(0.0)
            try:
                m.description = html.find(class_='col5').find_all('p')[0].text
            except (AttributeError, IndexError):
                m.description = ''

            raw_poster_html = html.find(class_='presentBlockImg')
            poster = re.search('(?<=\().+?(?=\))|$', str(raw_poster_html)).group()
            if poster:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urlopen(poster).read())
                img_temp.flush()
                m.poster.save(f"{external_id}.jpg", File(img_temp), save=False)
            else:
                m.poster = None
            m.save()

        return m

    @staticmethod
    def seasons(movie_external_id):
        s = Season.objects.filter(movie_id__external_id=movie_external_id)
        s_values = s.values_list('number', flat=True)
        html = collect_data(movie_external_id)

        raw_seasons_data = html.find_all(itemprop='season')

        for season in raw_seasons_data:
            season_number = season.find(class_='flat').text.split(' ')[0]
            if not int(season_number) in s_values:
                Season.objects.create(number=season_number, movie_id=movie_external_id)

            raw_episodes_data = season.find_all(itemprop='episode')
            existing_episodes = s.get(number=season_number).episodes.all().values_list('number', flat=True)
            episode_number = 1
            for episode in reversed(raw_episodes_data):
                if not episode_number in existing_episodes:
                    name = episode.find(itemprop='name').text
                    try:
                        date = parse(episode.find(itemprop='datePublished').text)
                    except ValueError:
                        date = None
                    Episode.objects.create(number=episode_number,
                                           name=name,
                                           date=date,
                                           movie_id=movie_external_id,
                                           season_id=s.get(number=season_number).id)
                episode_number += 1



# Collect data about all movies. It can takes for a long time, use it carefully
def full_data():
    main_page = requests.get(URL + 'search/all/')
    html = BeautifulSoup(main_page.text, "html.parser")

    pages_counter = html.find(class_='paginator').find_all('li')[-2].text
    for p_number in range(int(pages_counter) + 1):
        page = requests.get(URL + 'search/all/?page=' + str(p_number))
        page_html = BeautifulSoup(page.text, "html.parser")
        page_links = page_html.findAll('table')[1].findAll('tr')[1::]

        # collect all movies id on the page
        ids = re.findall('/(\d+)/', str(page_links))

        for id in ids:
            ParseInfo.movie(id)
            ParseInfo.seasons(id)