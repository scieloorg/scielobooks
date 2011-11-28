#!/usr/bin/env python
# encoding: utf-8

class Creator(object):
    def __init__(self, full_name, link_to_resume):
        self.full_name = full_name
        self.link_to_resume = link_to_resume


class IndividualAuthor(Creator):
    pass


class Chapter(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.__creators = []
        self.__title_translations = {}

    @property
    def creators(self):
        return self.__creators

    @property
    def title_translations(self):
        return self.__title_translations

    def __unicode__(self):
        return self.title if hasattr(self, 'title') else repr(self)


class Book(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.__chapters = []

    @property
    def chapters(self):
        return self.__chapters