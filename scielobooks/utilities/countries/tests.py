# coding: utf-8
import unittest
from countries import Countries

class CountriesTest(unittest.TestCase):

    def setUp(self):
        self.countries_pt = Countries('pt')
        self.countries_en = Countries('en')

    def test_get_localized_list(self):
        self.assertEqual(self.countries_pt['BR'], 'Brasil')
        self.assertEqual(self.countries_pt['CX'], 'Ilha do Natal')
        self.assertEqual(self.countries_en['BR'], 'Brazil')
        self.assertEqual(self.countries_en['CX'], 'Christmas Island')

    def test_get_unknown_country(self):
        with self.assertRaises(KeyError):
            self.countries_pt['kk']

    def test_iteration(self):
        for code in self.countries_pt:
            self.assertEqual(code, 'AF')
            break

    def test_unpacking_iteration(self):
        for code, country in self.countries_pt.items():
            self.assertEqual(code, 'AF')
            self.assertEqual(country, u'Afeganistão')
            break

    def test_contains(self):
        self.assertTrue('BR' in self.countries_pt)
        self.assertFalse('KK' in self.countries_pt)



#TODO:
# given the country name, return its code