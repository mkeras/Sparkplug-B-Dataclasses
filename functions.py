from .enums import MessageTypes
from time import time
from .exceptions import *

NAMESPACE = 'spBv1.0'


class Sequencer:
    def __init__(self, first: int = 0, last: int = 255):
        self.__first = first
        self.__last = last
        self.__current_seq = first - 1

    def __call__(self):
        self.__current_seq += 1
        if self.__current_seq > self.__last:
            self.reset()
            return self.__call__()
        return self.__current_seq

    def reset(self):
        self.__current_seq = self.__first - 1
        return self

    @property
    def current_value(self):
        return None if self.__current_seq < self.__first else self.__current_seq


def millis() -> int:
    return round(time()*1000)


def _filter_topic_str(string: str or None):
    if string is None:
        return
    for char in ['/', '+', '#']:
        if char in string:
            raise IllegalTopicCharError(char)


def encode_topic(message_type: MessageTypes,
                 scada_host_id: str = None,
                 group_id: str = None,
                 edge_node_id: str = None,
                 device_id: str = None) -> str:

    _filter_topic_str(scada_host_id)
    _filter_topic_str(group_id)
    _filter_topic_str(edge_node_id)
    _filter_topic_str(device_id)

    if message_type is MessageTypes.STATE:
        if not scada_host_id:
            raise SparkplugBError('"scada_host_id" is required for "STATE" message')
        return f'STATE/{scada_host_id}'
    elif not group_id or not edge_node_id:
        raise SparkplugBError(f'"group_id" and "edge_node_id" are required for "{message_type.value}" message')

    topic = f'{NAMESPACE}/{group_id}/{message_type.value}/{edge_node_id}'

    if message_type in [MessageTypes.DBIRTH,
                        MessageTypes.DDATA,
                        MessageTypes.DDEATH,
                        MessageTypes.DCMD]:
        if not device_id:
            raise SparkplugBError(f'"device_id" is required for "{message_type.value}" message')
        topic += '/' + device_id
    return topic


def decode_topic(topic: str) -> dict:
    topic_split = topic.split('/')
    topic_components = {'namespace': None,
                        'scada_host_id': None,
                        'group_id': None,
                        'edge_node_id': None,
                        'device_id': None,
                        'message_type': None}

    if topic.startswith('STATE/'):
        if len(topic_split) != 2:
            raise OutOfSpecError(f'topic "{topic}" is out of sparkplug B spec')
        topic_components['namespace'] = 'STATE'
        topic_components['scada_host_id'] = topic_split[1]
        topic_components['message_type'] = MessageTypes.STATE
        return topic_components

    if topic.startswith(NAMESPACE+'/'):
        if len(topic_split) not in [4, 5]:
            raise OutOfSpecError(f'topic "{topic}" is out of sparkplug B spec')
        elif len(topic_split) == 4 and topic_split[2] not in ['NBIRTH', 'NDEATH', 'NCMD', 'NDATA']:
            raise OutOfSpecError(f'topic "{topic}" is out of sparkplug B spec')
        elif len(topic_split) == 5:
            if topic_split[2] not in ['DBIRTH', 'DDEATH', 'DCMD', 'DDATA']:
                raise OutOfSpecError(f'topic "{topic}" is out of sparkplug B spec')
            topic_components['device_id'] = topic_split[4]

        topic_components['namespace'] = NAMESPACE
        topic_components['group_id'] = topic_split[1]
        topic_components['message_type'] = MessageTypes[topic_split[2]]
        topic_components['edge_node_id'] = topic_split[3]

        return topic_components
    raise OutOfSpecError(f'topic "{topic}" is out of sparkplug B spec')