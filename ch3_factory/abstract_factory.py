import abc
import urllib2

from BeautifulSoup import BeautifulSoup

class AbstractFactory(object):
    """ abstract factory interface provide three method at subclass
        create_protocol, create_port, create_parser
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, is_secure):
        """if is_secure true, factory uses secure connection"""
        self.is_secure = is_secure

    @abc.abstractmethod
    def create_protocol(self):
        pass

    @abc.abstractmethod
    def create_port(self):
        pass

    @abc.abstractmethod
    def create_parser(self):
        pass


class HTTPFactory(AbstractFactory):
    """ concrete factory to connect http"""

    def create_protocol(self):
        if self.is_secure:
            return 'https'
        else:
            return 'http'

    def create_port(self):
        if self.is_secure:
            return HTTPSecurePort()
        return HTTPPort()

    def create_parser(self):
        return HTTPParser()


class FTPFactory(AbstractFactory):
    """ factory to connect FTP"""
    def create_protocol(self):
        return 'ftp'

    def create_port(self):
        return FTPPort()

    def create_parser(self):
        return FTPParser()


class Port(object):
    __metaclass__ = abc.ABCMeta
    """ abstract product for connecting port. factory method create its subclass"""

    @abc.abstractmethod
    def __str__(self):
        pass


class HTTPPort(Port):
    """ concrete http port"""
    def __str__(self):
        return '80'


class HTTPSecurePort(Port):
    def __str__(self):
        return '443'


class FTPPort(Port):
    def __str__(self):
        return '21'


class Parser(object):
    """ abstract class for product which parsing web content"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __call__(self,content):
        pass


class HTTPParser(Parser):
    """ HTTP concrete parser"""
    def __call__(self,content):
        filenames = []
        soup = BeautifulSoup(content)
        links = soup.table.findAll('a')
        for link in links:
            filenames.append(link.text)
        return '\n'.join(filenames)


class FTPParser(Parser):
    def __call__(self, content):
        lines = content.split('\n')
        filenames = []
        for line in lines:
            splitted_line = line.split(None, 8)
            if len(splitted_line) == 9:
                filenames.append(splitted_line[-1])

        return '\n'.join(filenames)


class Connector(object):
    """Client"""
    def __init__(self,factory):
        """ Factory is instance of AbstractFactory, according to Factory class all connectors attributes created"""
        self.protocol = factory.create_protocol()
        self.port = factory.create_port()
        self.parse = factory.create_parser()

    def read(self, host, path):
        url = self.protocol + "://" + host + ":" + str(self.port) + path
        print 'Connecting to ',url
        return urllib2.urlopen(url,timeout=2).read()

    @abc.abstractmethod
    def parse(self):
        pass


if __name__ == "__main__":
    domain = 'ftp.freebsd.org'
    path = '/pub/FreeBSD/'

    protocol = input('Connecting to {}. Which Protocol to use? (0-http, 1-ftp'.format(domain))

    if protocol == 0:
        is_secure = bool(input('Use secure connection? (1-yes, 0-no): '))
        factory = HTTPFactory(is_secure)
    elif protocol == 1:
        is_secure = False
        factory = FTPFactory(is_secure)
    else:
        print 'Sorry, wrong answer'

    connector = Connector(factory)
    try:
        content = connector.read(domain,path)
    except urllib2.URLError, e:
        print 'Can not access resource with this method'
    else:
        print connector.parse(content)
