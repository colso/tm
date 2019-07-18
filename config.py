#!/usr/bin/python

import os
import configparser

class Empty:
    pass

def getValue(value):
    try:
        if value[0] == '/':
            evalValue = value
        else:
            evalValue = eval(value)
        if type(evalValue) in [int, float, list, tuple, dict, str]:
            return evalValue
    except NameError:
        pass
    return value

class TwalConfig:
    def __init__(self, configFilename, debug = False):
        self.debug = debug
        self.filename = os.path.join(os.path.split(__file__)[0], configFilename)
        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda option: option
        self.config.read(self.filename)
        print("Load Config : %s" % self.filename)

        for section in self.config.sections():
            if self.debug is True:
                print("[%s]" % section)
            if not hasattr(self, section):
                setattr(self, section, Empty())

            current_section = getattr(self, section)
            for option in self.config[section]:
                value = self.config.get(section, option)
                if self.debug is True:
                    print("%s = %s" % (option, value))
                setattr(current_section, option, getValue(value))
                #setattr(current_section, option, value)

    def getValue(self, section, option):
        return getValue(self.config[section][option])

    def setValue(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][option] = str(value)

        if not hasattr(self, section):
            setattr(self, section, Empty())
        current_section = getattr(self, section)
        setattr(current_section, option, value)

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
            print("Saverd Config : " + self.filename)

    def getFilename(self):
        return self.filename

#------------------------------------------------------------------------------

#if __name__ != '__main__':
#	import unittest
#
#	class test(unittest.TestCase):
#		def testConfig(self):
#			# load test
#			testConfig = Config("torr.ini", debug=False)
#
##			# set value
##			testConfig.setValue("TestSection", "test_int", 45)
##			testConfig.setValue("TestSection", "test_float", 0.1)
##			testConfig.setValue("TestSection", "test_string", "Hello, World")
##			testConfig.setValue("TestSection", "test_list", [1, 2, 3])
##			testConfig.setValue("TestSection", "test_tuple", (4, 5, 6))
##			testConfig.setValue("TestSection", "test_dict", {"x":7.0, "y":8.0})
##
#				# call test
##			self.assertEqual(testConfig.TestSection.test_int, 45)
##			self.assertEqual(testConfig.TestSection.test_float, 0.1)
##			self.assertEqual(testConfig.TestSection.test_string, "Hello, World")
##			self.assertEqual(testConfig.TestSection.test_list, [1, 2, 3])
##			self.assertEqual(testConfig.TestSection.test_tuple, (4, 5, 6))
##			self.assertEqual(testConfig.TestSection.test_dict['x'], 7.0)
##			self.assertEqual(testConfig.TestSection.test_dict['y'], 8.0)
#
#			print(testConfig.GENERAL.download_path)
#
#				# set value test
#			testConfig.setValue("TestSection", "test_int", 99)
#			self.assertEqual(testConfig.TestSection.test_int, 99)
#
#			testConfig.save()
#	unittest.main()
#				
