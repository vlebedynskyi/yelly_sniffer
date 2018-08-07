import logging
import random

from bs4 import BeautifulSoup
from .network import do_get

logger = logging.getLogger(__name__)
PAGES_PATTERN = "{site}/page/{page}"


def process_sites(sites, count_per_site):
    logger.debug("Looking for pages to get links from")
    pages = generate_pages_links(sites, count_per_site)
    logger.debug("Next pages generated:\n\t\t\t\t\t\t\t\t\t%s", '\n\t\t\t\t\t\t\t\t\t'.join(map(str, pages)))

    logger.debug("Looking for links to parse from")
    links = []
    random.shuffle(pages)
    for page in pages:
        try:
            link = generate_link_from_page(page)
            links.append(link)
        except BaseException as e:
            logger.exception("Unable to generate link", e)
    logger.debug("Next links found:\n\t\t\t\t\t\t\t\t\t%s", '\n\t\t\t\t\t\t\t\t\t'.join(map(str, links)))

    posts = []
    random.shuffle(links)
    for link in links:
        try:
            logger.debug("Parsing post %s", link)
            post = parse_post(link)
            if post.image:
                posts.append(post)
            else:
                logger.warning("No image for post,  %s", post.title)
        except BaseException as e:
            logger.error("Unable to parse", e)

    return posts


def generate_link_from_page(link):
    logger.debug("Getting link from page %s", link)

    # parser.find_all("article")[0].find("a").get("href")
    page = do_get(link)
    parser = BeautifulSoup(page, 'html.parser')

    post = random.choice(parser.find_all("article"))
    return post.find("a").get("href")


def generate_pages_links(sites, count_per_site):
    pages = []
    for site in sites:
        logger.debug("Getting page from site " + site)
        pages_count = get_page_count(site)
        for count in range(count_per_site):
            pages.append(PAGES_PATTERN.format(site=site, page=random.randint(1, pages_count)))

    return pages


def get_page_count(site):
    page = do_get(site)
    parser = BeautifulSoup(page, 'html.parser')
    pages_numbers = parser.find_all("a", "page-numbers")
    biggest_number = 0
    for i in range(len(pages_numbers)):
        try:
            number = int(pages_numbers[i].get_text())
            if number > biggest_number:
                biggest_number = number
        except Exception as e:
            pass

    logger.debug("Site %s has %s pages", site, biggest_number)
    return biggest_number


def parse_post(link):
    post = do_get(link)
    parser = BeautifulSoup(post, 'html.parser', from_encoding="utf-8")

    post_title = parser.find("h1", {"class": "entry-title"}).get_text()
    content = parser.find("div", {"class": "entry-content"})

    # Add some clean ip of content

    for ins in content.find_all("ins", {'class': 'adsbygoogle'}):
        ins.decompose()

    for ins in content.find_all("div", {'class': 'nodesktop'}):
        ins.decompose()

    for ins in content.find_all("div", {'class': 'ads'}):
        ins.decompose()

    for ins in content.find_all("div", {'class': 'nomobile'}):
        ins.decompose()

    for ins in content.find_all("div", {'class': 'r-bl'}):
        ins.decompose()

    for ins in content.find_all("script"):
        ins.decompose()

    for ins in content.find_all("center"):
        ins.decompose()

    for ins in content.find_all("div", {'class': 'panel'}):
        ins.name = "p"

    feature_image = None
    for img in content.find_all("img"):
        feature_image = img["src"]
        img["alt"] = post_title
        img["class"] = "aligncenter size-full"
        img["sizes"] = None
        img["srcset"] = None

    return YellyPost(post_title, content.renderContents().decode("utf8"), feature_image)


class YellyPost:
    def __init__(self, title, body, image_url):
        self.title = title
        self.body = body
        self.image = image_url
