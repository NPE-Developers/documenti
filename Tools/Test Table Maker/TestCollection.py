import codecs
import json
from collections import OrderedDict
import re
import os.path


class TestIterator:
    def __init__(self, section):
        self.tests = section['tests']
        self.current_element = 0
        self.id_counter = 0
        self.id_config = section['id_config']
        self.skip_not_approved = section['skip_not_approved']
        self.place_holders = []
        for place_holder in re.findall(r"\[\w+\]", self.id_config, re.IGNORECASE):
            place_holder = place_holder.replace('[', '').replace(']', '')
            if len(place_holder) > 0:
                self.place_holders.append(place_holder)

    # Iterator logic
    def __iter__(self):
        return self

    def __next__(self):
        if self.current_element >= len(self.tests):
            raise StopIteration
        else:
            if self.skip_not_approved:
                while self.current_element < len(self.tests) and not self.tests[self.current_element]['approved']:
                    self.current_element += 1
                if self.current_element >= len(self.tests):
                    raise StopIteration

            index = self.current_element
            self.current_element += 1
            return self._generateId(), self.tests[index]

    def _generateId(self):
        self.id_counter += 1
        computed_id = self.id_config.replace('#POS#', str(self.id_counter))
        current_test = self.tests[self.current_element - 1]
        for place_holder in self.place_holders:
            if place_holder in current_test:
                computed_id = computed_id.replace('[' + place_holder + ']', current_test[place_holder])
        return computed_id


class SectionIterator:
    def __init__(self, tests):
        self.sections = list(tests.keys())
        self.tests = tests
        self.current = 0

    # Iterator logic
    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.sections):
            raise StopIteration
        else:
            index = self.current
            self.current += 1
            return self.sections[index], TestIterator(self.tests[self.sections[index]])


class TestCollection:
    tests_file = "test.json"

    def __init__(self):
        self.tests = {}

    def load(self):
        ok = False
        # Check if file exists
        if not os.path.exists(self.tests_file):
            file = open(self.tests_file, 'w')
            file.write('{}')
            file.close()
        # Open and parse the file
        with codecs.open(self.tests_file, 'r', "utf-8") as data_file:
            try:
                # Load the json file to the ram.
                self.tests = json.load(data_file, object_pairs_hook=OrderedDict)
                ok = True
            except json.decoder.JSONDecodeError:
                # Shit happens
                print('Errore di sintassi nel file: ' + self.tests_file)

        return ok

    def __iter__(self):
        return SectionIterator(self.tests)