from common import config
import news_page_object as news
import argparse
import logging
import re
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO)


is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')
logger = logging.getLogger(__name__)


def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']

    logging.info(f'\033[1;31;40m Beginning scraper for {host} \033[0;37;40m')
    homepage = news.HomePage(news_site_uid, host)

    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)
        if article:
            logger.info("Article fetched!!")
            print(f"\033[1;32;40m {article.title} \033[0;37;40m")
            articles.append(article)

    print(
        f"\n \033[1;33;40mNUMERO DE ARTICULOS OBTENIDOS: {len(articles)} \033[0;37;40m")


def _fetch_article(news_site_uid, host, link):
    builded_link = _build_link(host, link)
    logger.info(
        f"\033[1;36;40m Start fetching article at {builded_link} \033[0;37;40m")

    article = None
    try:
        article = news.ArticlePage(news_site_uid, builded_link)
    except(HTTPError, MaxRetryError) as e:
        logger.warning('Error Fetching the article', exc_info=False)

    if article and not article.body:
        logger.warning('Invalid article, There is no body')
        return None

    return article


def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return f"{host}{link}"
    else:
        return f"{host}/{link}"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                        help='The news site that you want to scrape',
                        type=str,
                        choices=news_site_choices)

    args = parser.parse_args()
    _news_scraper(args.news_site)
