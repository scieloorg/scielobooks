#!/usr/bin/env python
# encoding: utf-8
import unittest
from domain import IndividualAuthor
from domain import Chapter
from domain import Book


class testChapter(unittest.TestCase):

    def __basic_chapter(self):
        chapter = Chapter()
        chapter.title = u'Tópicos avançados'
        chapter.title_translations['us_EN'] = 'Advanced Topics'

        return chapter

    def test_basic(self):
        attrs = {'title': u'Introdução ao estudo da emancipação política do Brasil',}
        chapter = Chapter(**attrs)

        self.assertEqual(chapter.title, attrs['title'])

    def test_creator(self):
        emilia = IndividualAuthor(u'Costa, Emília Viotti da', u'http://pt.wikipedia.org/wiki/Emília_Viotti_da_Costa')
        chapter = self.__basic_chapter()

        chapter.creators.append(emilia)

        self.assertEqual(len(chapter.creators), 1)
        self.assertEqual(chapter.creators[0].full_name, u'Costa, Emília Viotti da')
        self.assertEqual(chapter.creators[0].link_to_resume, u'http://pt.wikipedia.org/wiki/Emília_Viotti_da_Costa')

    def test_translated_title(self):
        chapter = self.__basic_chapter()

        self.assertEqual(chapter.title, u'Tópicos avançados')
        self.assertEqual(chapter.title_translations['us_EN'], 'Advanced Topics')

    def test_translated_title_deletion(self):
        chapter = self.__basic_chapter()

        self.assertEqual(chapter.title_translations['us_EN'], 'Advanced Topics')
        del(chapter.title_translations['us_EN'])
        self.assertFalse('us_EN' in chapter.title_translations)

    def test_unicode(self):
        chapter = self.__basic_chapter()
        # Chapter without title attribute
        chapter2 = Chapter()

        self.assertEqual(unicode(chapter), u'Tópicos avançados')
        self.assertTrue(unicode(chapter2).startswith('<domain.Chapter'))


class testBook(unittest.TestCase):

    def __basic_book(self):
        attrs = {'title': u'Gödel, Escher, Bach: An Eternal Golden Braid'}
        book = Book(**attrs)

        return book

    def test_basic(self):
        book = self.__basic_book()

        self.assertEquals(book.title, u'Gödel, Escher, Bach: An Eternal Golden Braid')

    def test_chapter(self):
        book = self.__basic_book()
        chapter = Chapter()
        chapter.title = u'Tópicos avançados'
        chapter.title_translations['us_EN'] = 'Advanced Topics'
        book.chapters.append(chapter)

        self.assertEqual(len(book.chapters), 1)
