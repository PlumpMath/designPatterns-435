import pickle


class Url(object):
    @classmethod
    def shorten(cls, full_url):
        """ Shorten full url"""

        # Create Url Class instance
        instance = cls()
        instance.full_url = full_url
        instance.short_url = instance.__create_short_url()
        Url.__save_url_mapping(instance)
        return instance

    @classmethod
    def get_by_short_url(cls,short_url):
        """return url instance,corresponnding to short_url of None if not found"""
        url_mapping = Url.__load_url_mapping()
        return url_mapping.get(short_url)

    def __create_short_url(self):
        """create short url. save and return it"""
        last_short_url = Url.__load_last_short_url()
        short_url = self.__increment_string(last_short_url)
        Url.__save_last_short_url(short_url)
        return short_url

    def __increment_string(self,string):
        """increment string:
            a -> b
            z -> aa
            az -> ba
            empty -> a
        """
        if string == '':
            return 'a'

        last_char = string[-1]

        if last_char != 'z':
            return string[:-1] + chr(ord(last_char) + 1)

        return self.__increment_string(string[:-1]) + 'a' #when last is 'z'

    @staticmethod
    def __load_last_short_url():
        """ return last created shorten url"""
        try:
            return pickle.load(open("last_short.p","rb"))
        except IOError:
            return ''

    @staticmethod
    def __save_last_short_url(url):
        """save last created short url"""
        pickle.dump(url,open("last_short.p","wb"))

    @staticmethod
    def __load_url_mapping():
        """return short url mapping url instance"""
        try:
            return pickle.load(open("short_to_url.p","rb"))
        except IOError:
            return {}

    @staticmethod
    def __save_url_mapping(instance):
        """save short_url mapping to url instance"""
        short_to_url = Url.__load_url_mapping()
        short_to_url[instance.short_url] = instance
        pickle.dump(short_to_url,open("short_to_url.p","wb"))