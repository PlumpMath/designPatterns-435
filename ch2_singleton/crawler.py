import httplib2
import os
import re
import threading
import urllib
from urlparse import urlparse,urljoin
from BeautifulSoup import BeautifulSoup


class Singleton(object):
    def __new__(cls):
        if not hasattr(cls,'instance'):
            cls.instance = super(Singleton,cls).__new__(cls)
        return cls.instance


class ImageDownladerThread(threading.Thread):
    """ parallel down Image thread"""
    def __init__(self,thread_id, name, counter):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print 'Starting thread', self.name
        download_images(self.name)
        print "finished thread ", self.name


def traverse_site(max_links=10):
    link_parser_singleton = Singleton()

    # while queue has parsing page
    while link_parser_singleton.queue_to_parse:
        if len(link_parser_singleton.to_visit) == max_links:
            return

        url = link_parser_singleton.queue_to_parse.pop()

        http = httplib2.Http()
        try:
            status, response = http.request(url)
        except Exception:
            continue

        # if not web page, pass
        if  status.get('content-type') .find('text/html'):
            continue

        # to download image, add link to the queue
        link_parser_singleton.to_visit.add(url)
        print 'Added', url, 'to queue'

        bs = BeautifulSoup(response)

        for link in BeautifulSoup.findAll(bs, 'a'):

            link_url = link.get('href')

            # <img> has no href?
            if not link_url:
                continue

            parsed = urlparse(link_url)

            # if link connect to external web pages, continue
            if parsed.netloc and parsed.netloc != parsed_root.netloc:
                continue

            # reletive link to absolute link
            link_url = (parsed.scheme or parsed_root.scheme) + '://' + \
                       (parsed.netloc or parsed_root.netloc) + parsed.path or ''

            # continue when duplicated link
            if link_url in link_parser_singleton.to_visit:
                continue

            # add link to parsing (add to left)
            link_parser_singleton.queue_to_parse = [link_url] + link_parser_singleton.queue_to_parse


def download_images(thread_name):
    singleton = Singleton()
    # while pages to download is left
    while singleton.to_visit:

        url = singleton.to_visit.pop()

        http = httplib2.Http()
        print thread_name, 'Starting downloading images from', url

        try:
            status, response = http.request(url)
        except Exception:
            continue

        bs = BeautifulSoup(response)

        # find All <img> tags
        images = BeautifulSoup.findAll(bs,'img')

        if __name__ == '__main__':
            for image in images:
                # absolute or relative address url
                src = image.get('src')
                """ make entire url. if url is relative,
                expand with webpage domain.
                if url is absolute, just go
              """
                src = urljoin(url,src)

                # get base name
                basename = os.path.basename(src)

                if src not in singleton.downloaded:
                    singleton.downloaded.add(src)
                    print "Downloading", src
                    # download to local
                    urllib.urlretrieve(src,os.path.join('images', basename))

            print thread_name, 'finished downloading images from', url

if __name__ == '__main__':
    root = 'http://python.org'

    parsed_root = urlparse(root)

    singleton = Singleton()
    singleton.queue_to_parse = [root]
    # url set to download
    singleton.to_visit = set()
    # downloaded iamges
    singleton.downloaded = set()

    traverse_site()

    # if no image dir, make it
    if not os.path.exists('images'):
        os.makedirs('images')

    # thread creation
    thread1 = ImageDownladerThread(1, 'Thread-1', 1)
    thread2 = ImageDownladerThread(2, 'Thread-2', 2)

    # create new thread
    thread1.start()
    thread2.start()