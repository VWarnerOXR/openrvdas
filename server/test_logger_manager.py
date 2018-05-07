#!/usr/bin/env python3

import json
import logging
import sys
import tempfile
import threading
import time
import unittest
import warnings

sys.path.append('.')

from logger.readers.network_reader import NetworkReader
from server.logger_manager import LoggerManager

sample_data = [
  'Permission is hereby granted, free of charge, to any person obtaining a copy',
  'of this software and associated documentation files (the "Software"), to deal',
  'in the Software without restriction, including without limitation the rights',
  'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell',
  'copies of the Software, and to permit persons to whom the Software is',
  'furnished to do so, subject to the following conditions:'
]

sample_cruise = {
  "cruise": {
    "id": "NBP1700",
    "start": "2017-01-01",
    "end": "2017-02-01"
  },
  "loggers": {
    "sample": {
      "configs": ["off", "sample->net"]
    },
  },
  "modes": {
    "off": {
      "sample": "off",
    },
    "port": {
      "sample": "sample->net"
    }
  },
  "default_mode": "off",
  "configs": {
    "off": {},
    "sample->net": {
      "name": "sample->net",
      "readers": {
        "class": "TextFileReader",
        "kwargs": {"interval": 0.5,
                   "file_spec": "fill this in" }
      },
      "transforms": {
        "class": "PrefixTransform",
        "kwargs": {"prefix": "TestLoggerManager"}
      },
      "writers": {
        "class": "NetworkWriter",
        "kwargs": {"network": ":6220"}
      }
    },
    "sample->file": {
      "name": "sample->file",
      "readers": {
        "class": "TextFileReader",
        "kwargs": {"interval": 0.5,
                   "file_spec": "fill this in" }
      },
      "transforms": {
        "class": "PrefixTransform",
        "kwargs": {"prefix": "TestLoggerManager"}
      },
      "writers": {
        "class": "TextFileWriter",
        "kwargs": {"filename": "fill this in"}
      }
    }
  },
  "default_mode": "off"
}


################################################################################
class TestLoggerManagerAPI(unittest.TestCase):
  ############################
  def setUp(self):
    warnings.simplefilter("ignore", ResourceWarning)

    self.tmpdir = tempfile.TemporaryDirectory()
    self.tmpdirname = self.tmpdir.name
    logging.info('created temporary directory "%s"', self.tmpdirname)

    self.input_filename = self.tmpdirname + '/input.txt'
    self.output_filename = self.tmpdirname + '/output.txt'
    self.cruise_filename = self.tmpdirname + '/cruise.json'
    
    sample_cruise['configs']['sample->net']['readers']['kwargs']['file_spec'] \
      = self.input_filename
    sample_cruise['configs']['sample->file']['readers']['kwargs']['filename'] \
      = self.output_filename

    logging.info('Creating temp input file %s', self.input_filename)
    with open(self.input_filename, 'w') as f:
      for line in sample_data:
        f.write(line + '\n')

    logging.info('Creating temp cruise file %s', self.cruise_filename)
    with open(self.cruise_filename, 'w') as f:
      f.write(json.dumps(sample_cruise, indent=4))
    
  ############################
  def test_basic(self):

    ############################
    def network_reader():
      reader = NetworkReader(network=':6220')
      for i in range(4):
        self.assertEqual(reader.read(), 'TestLoggerManager ' + sample_data[i])
      logging.info('NetworkReader done')

    ############################
    def run_commands(logger_manager):
      time.sleep(1)
      logger_manager.process_command('load_cruise %s' % self.cruise_filename)
      logger_manager.process_command('set_mode port')      
      time.sleep(2.5)
      logger_manager.process_command('quit')

    ############################
    def run_commands(logger_manager):
      time.sleep(1)
      logger_manager.process_command('load_cruise %s' % self.cruise_filename)
      logger_manager.process_command('set_mode port')      
      time.sleep(2.5)
      logger_manager.process_command('quit')

    ###############################
    # Create LoggerManager and test it
    logger_manager = LoggerManager()

    network_reader_thread = threading.Thread(target=network_reader)
    network_reader_thread.start()
    
    command_thread = threading.Thread(target=run_commands,
                                      args=(logger_manager,))
    command_thread.start()

    logger_manager.run()

    network_reader_thread.join()
    command_thread.join()
    
################################################################################
if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-v', '--verbosity', dest='verbosity',
                      default=0, action='count',
                      help='Increase output verbosity')
  args = parser.parse_args()

  LOGGING_FORMAT = '%(asctime)-15s %(message)s'
  logging.basicConfig(format=LOGGING_FORMAT)

  LOG_LEVELS ={0:logging.WARNING, 1:logging.INFO, 2:logging.DEBUG}
  args.verbosity = min(args.verbosity, max(LOG_LEVELS))
  logging.getLogger().setLevel(LOG_LEVELS[args.verbosity])
  
  #logging.getLogger().setLevel(logging.DEBUG)
  unittest.main(warnings='ignore')
    
