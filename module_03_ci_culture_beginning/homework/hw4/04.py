import unittest
import datetime


class Person:
    def __init__(self, name, year_of_birth, address=''):
        self.name = name
        self.yob = year_of_birth
        self.address = address

    def get_age(self):
        now = datetime.datetime.now()
        return now.year - self.yob

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def is_homeless(self):
        return self.address is None or self.address == ""


class TestPerson(unittest.TestCase):

    def test_init(self):
        person = Person("Иван", 1990, "Москва")
        self.assertEqual(person.name, "Иван")
        self.assertEqual(person.yob, 1990)
        self.assertEqual(person.address, "Москва")

        person2 = Person("Петр", 1985)
        self.assertEqual(person2.name, "Петр")
        self.assertEqual(person2.yob, 1985)
        self.assertEqual(person2.address, "")

    def test_get_name(self):
        person = Person("Мария", 1995)
        self.assertEqual(person.get_name(), "Мария")

    def test_set_name(self):
        person = Person("СтароеИмя", 1990)
        person.set_name("НовоеИмя")
        self.assertEqual(person.name, "НовоеИмя")

    def test_get_age(self):
        person = Person("Иван", 1990)
        current_year = datetime.datetime.now().year
        expected_age = current_year - 1990
        self.assertEqual(person.get_age(), expected_age)

        self.assertGreaterEqual(person.get_age(), 0)

    def test_set_address(self):
        person = Person("Иван", 1990)
        person.set_address("Санкт-Петербург")
        self.assertEqual(person.address, "Санкт-Петербург")

    def test_get_address(self):
        person = Person("Иван", 1990, "Казань")
        self.assertEqual(person.get_address(), "Казань")

        person2 = Person("Петр", 1985)
        self.assertEqual(person2.get_address(), "")

    def test_is_homeless(self):
        person = Person("Иван", 1990)
        self.assertTrue(person.is_homeless())

        person2 = Person("Петр", 1985, "Москва")
        self.assertFalse(person2.is_homeless())

        person3 = Person("Мария", 1995, "")
        self.assertTrue(person3.is_homeless())

        person4 = Person("Анна", 2000, None)
        self.assertTrue(person4.is_homeless())


if __name__ == '__main__':
    unittest.main()