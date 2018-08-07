import logging
import os

from wordpress_xmlrpc import Client, WordPressPost, xmlrpc_client
from wordpress_xmlrpc.methods import media as wp_media
from wordpress_xmlrpc.methods import users as wp_users
from wordpress_xmlrpc.methods import posts as wp_posts

from yelly import yelly
from yelly import mails
from yelly import tools
from yelly import network
from configparser import RawConfigParser

CONFIG_FILE = 'config.ini'
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOG_FILE = 'logs/yelly_sniff.log'

# Initialize logger
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, filename=LOG_FILE, filemode='a')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logging.getLogger('').addHandler(console_handler)
logger = logging.getLogger(__name__)


def send_posts_as_mail(sender, sender_pass, recipient, posts_to_send):
    logger.debug("Sending posts to %s via e-mail", recipient)
    for p in posts_to_send:
        logger.debug("Sending %s, to %s", p.title, recipient)
        mails.send(sender, sender_pass, recipient, p.title, p.body, p.image)


def send_posts_xmlrpc(wp_server, wp_user, wp_user_pass, posts_to_send):
    logger.debug("Sending posts to %s via xmlrpc", server)
    logger.debug("Connecting to server %s", wp_server)
    wp = Client(wp_server, wp_user, wp_user_pass)
    user = wp.call(wp_user.GetUserInfo())
    if user:
        logger.debug("Connected successfully. User is %s", user.username)
    else:
        return

    for p in posts_to_send:
        logger.debug("Sending %s", p.title)
        logger.debug("Uploading image")
        data = {'name': 'picture.jpg', 'type': 'image/jpeg'}
        with open(p.image, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())
        uploaded_image = wp.call(wp_media.UploadFile(data))

        wp_post = WordPressPost()
        wp_post.title = p.title
        wp_post.content = p.body
        wp_post.thumbnail = uploaded_image['id']
        wp_post.post_status = "draft"  # TODO fix it
        wp.call(wp_posts.NewPost(wp_post))

if __name__ == "__main__":
    logger.debug("---------------------------------------------------------------------------------------")
    logger.debug("Running Yelly sniffer")

    logger.debug("Preparing configs from file %s", os.path.abspath(LOG_FILE))

    config = RawConfigParser()
    config.read(CONFIG_FILE)

    sites = config.get("SNIFF", "SITES")
    count = config.getint("SNIFF", "POSTS_PER_SITE")
    publish_method = config.get("SNIFF", "PUBLISH_METHOD")
    dump_folder = config.get("SNIFF", "DUMP_FOLDER")

    logger.debug("Start parsing...")
    posts = yelly.process_sites(sites.split(","), count)
    logger.debug("Parsing finished, Dumping posts to disk %s", os.path.abspath(dump_folder))
    for post in posts:
        if post.title and post.body:
            try:
                logger.debug("Dumping %s", post.title)
                tools.dump_to_file(os.path.join(dump_folder, u'{}.html'.format(post.title)), post.body)
                image_path = os.path.join(dump_folder, u'{}.jpeg'.format(post.title))
                network.download_file(post.image, image_path)
                post.image = image_path
            except BaseException as e:
                posts.remove(post)
                logger.exception("error while dumping %s", post.title, e)

    publish_method = config.get("SNIFF", "PUBLISH_METHOD")
    logger.debug("Publish method = %s", publish_method)
    if publish_method == "PUBLISH_MAIL":
        mail_sender = config.get("PUBLISH_MAIL", "MAIL_SENDER")
        mail_pass = config.get("PUBLISH_MAIL", "MAIL_SENDER_PASS")
        mail_recipient = config.get("PUBLISH_MAIL", "MAIL_RECIPIENT")
        send_posts_as_mail(mail_sender, mail_pass, mail_recipient, posts)
    elif publish_method == "PUBLISH_XML_RPC":
        server = config.get("PUBLISH_XML_RPC", "WP_XMLRPC_PATH")
        server_user = config.get("PUBLISH_XML_RPC", "WP_USER_NAME")
        server_user_pass = config.get("PUBLISH_XML_RPC", "WP_USER_PASS")
        send_posts_xmlrpc(server, server_user, server_user_pass, posts)
    else:
        exit(0)
