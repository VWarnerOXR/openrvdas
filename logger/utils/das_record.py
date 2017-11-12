#!/usr/bin/env python3

"""DASRecord is a structured representation of the field names and
values (and metadata) contained in a sensor record.

If a json string is passed, it is parsed into a dictionary and its
values for timestamp, fields and metadata are copied in. Otherwise,
the DASRecord object is initialized with the passed-in values for
instrument, timestamp, fields (a dictionary of fieldname-value pairs)
and metadata.

If timestamp is not specified, the instance will use the current time.
"""

import json

from utils.read_json import parse_json
from logger.utils.timestamp import timestamp as timestamp_method

################################################################################
class DASRecord:
  ############################
  def __init__(self, json=None, data_id=None, message_type=None,
               timestamp=0, fields={}, metadata={}):
    if json:
      parsed = parse_json(json)
      self.data_id = parsed.get('data_id', None)
      self.message_type = parsed.get('message_type', None)
      self.timestamp = parsed.get('timestamp', None)
      self.fields = parsed.get('fields', {})
      self.metadata = parsed.get('metadata', {})
    else:
      #self.source = 
      self.data_id = data_id
      self.message_type = message_type
      self.timestamp = timestamp or timestamp_method()
      self.fields = fields
      self.metadata = metadata

  ############################
  def as_json(self):
    json_dict = {
      'data_id': self.data_id,
      'message_type': self.message_type,
      'timestamp': self.timestamp,
      'fields': self.fields,
      'metadata': self.metadata
    }
    return json.dumps(json_dict)

  ############################
  def __str__(self):
    return ('{\'data_id\': \'%s\', \'message_type\': \'%s\', '
            '\'timestamp\': %f, \'fields\':%s, \'metadata\': %s }'
            % (self.data_id, self.message_type, 
               self.timestamp, self.fields, self.metadata))
  
