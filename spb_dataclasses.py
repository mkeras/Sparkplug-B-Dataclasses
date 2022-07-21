from .protobuf import sparkplug_b_pb2
from .enums import SpecialValues, MessageTypes, DataTypes
from dataclasses import dataclass, field, asdict, fields
from typing import List
from enum import Enum
import json
    

@dataclass(frozen=True)
class Metadata:
    pass


@dataclass(frozen=True)
class Properties:
    pass


@dataclass(frozen=True)
class DataSet:
    pass


@dataclass(frozen=True)
class Template:
    pass


@dataclass(frozen=True)
class MetricValueExtension:
    pass


@dataclass(frozen=True)
class Metric:
    name: str = SpecialValues.DO_NOT_SERIALIZE
    alias: int = SpecialValues.DO_NOT_SERIALIZE
    timestamp: int = SpecialValues.DO_NOT_SERIALIZE
    datatype: DataTypes = SpecialValues.DO_NOT_SERIALIZE
    is_historical: bool = SpecialValues.DO_NOT_SERIALIZE
    is_transient: bool = SpecialValues.DO_NOT_SERIALIZE
    is_null: bool = SpecialValues.DO_NOT_SERIALIZE
    metadata: Metadata = SpecialValues.DO_NOT_SERIALIZE
    properties: Properties = SpecialValues.DO_NOT_SERIALIZE

    value: any = field(default=SpecialValues.DO_NOT_SERIALIZE)

    int_value: int = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    long_value: int = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    float_value: float = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    double_value: float = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    boolean_value: bool = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    string_value: str = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    bytes_value: bytes = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)

    dataset_value: DataSet = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    template_value: Template = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)
    extension_value: MetricValueExtension = field(default=SpecialValues.DO_NOT_SERIALIZE, init=False)

    def __post_init__(self):
        if isinstance(self.datatype, str):
            print('string to enum')
            object.__setattr__(self, 'datatype', DataTypes[self.datatype])
        if self.is_null is not True and self.value is not SpecialValues.DO_NOT_SERIALIZE:
            object.__setattr__(self, self._get_datatype_str(), self.value)
        object.__setattr__(self, 'value', SpecialValues.DO_NOT_SERIALIZE)

    def _get_datatype_str(self) -> str:
        print(type(self.datatype), type(DataTypes.Float))
        if self.datatype in [DataTypes.Int8, DataTypes.Int16, DataTypes.Int32,
                             DataTypes.UInt8, DataTypes.UInt16, DataTypes.UInt32]:
            return 'int_value'
        elif self.datatype in [DataTypes.Int64, DataTypes.UInt64, DataTypes.DateTime]:
            return 'long_value'
        elif self.datatype is DataTypes.Float:
            return 'float_value'
        elif self.datatype is DataTypes.Double:
            return 'double_value'
        elif self.datatype is DataTypes.Boolean:
            return 'boolean_value'
        elif self.datatype in [DataTypes.Text, DataTypes.String, DataTypes.JSONString, DataTypes.UUID]:
            return 'string_value'
        elif self.datatype in [DataTypes.Bytes, DataTypes.File, DataTypes.JSONBytes]:
            return 'bytes_value'
        elif self.datatype is DataTypes.DataSet:
            return 'dataset_value'
        elif self.datatype is DataTypes.Template:
            return 'template_value'

        raise ValueError(f'{self.datatype} is invalid datatype')


@dataclass(frozen=True)
class Payload:
    timestamp: int
    seq: int
    metrics: List[Metric] = SpecialValues.DO_NOT_SERIALIZE
    uuid: str = SpecialValues.DO_NOT_SERIALIZE
    body: bytes = SpecialValues.DO_NOT_SERIALIZE

    def __post_init__(self):
        def extract_values(val):
            if isinstance(val, Enum):
                return val.value
            return val

        def dict_factory(dataclass_):
            return {k: extract_values(v) for k, v in dataclass_ if v is not SpecialValues.DO_NOT_SERIALIZE}
        self_dict = asdict(self, dict_factory=dict_factory)
        object.__setattr__(self, '_dict_form', self_dict)

    def serialize(self) -> bytes:
        """ output the dataclass into a protobuf serialized string of bytes """
        protobuf_payload = sparkplug_b_pb2.Payload()

        def fill_payload(data: dict, protobuf_obj):
            for key, value in data.items():
                if isinstance(value, list):
                    for list_value in value:
                        sub_protobuf_item = getattr(protobuf_obj, key).add()
                        fill_payload(list_value, sub_protobuf_item)
                elif isinstance(value, dict):
                    raise NotImplementedError
                else:
                    setattr(protobuf_obj, key, value)

        fill_payload(self._dict_form, protobuf_payload)
        return protobuf_payload.SerializeToString()

    def to_json_str(self) -> str:
        return json.dumps(self._dict_form)

    def to_dict(self) -> dict:
        return self._dict_form

    def validate(self, message_type: MessageTypes):
        """ validate for required parameters based on message type """
        raise NotImplementedError

    @classmethod
    def from_mqtt_payload(cls, payload: bytes):
        """ create a Payload dataclass by deserializing a raw mqtt binary payload """
        protobuf_payload = sparkplug_b_pb2.Payload()
        protobuf_payload.ParseFromString(payload)

        values = {}

        for field_ in fields(cls):
            if field_.name == 'metrics':
                values['metrics'] = []
                for metric_ in getattr(protobuf_payload, 'metrics'):
                    metric_data = {}
                    for metric_field in fields(Metric):
                        if metric_.HasField(metric_field.name) and not metric_field.name.endswith('_value'):
                            if metric_field.name in ['metadata', 'properties']:
                                raise NotImplementedError
                            if metric_field.name == 'value':
                                value_key = metric_.WhichOneof("value")
                                if value_key in ['dataset_value', 'template_value', 'extension_value']:
                                    raise NotImplementedError
                                metric_data['value'] = getattr(metric_, value_key)
                                continue
                            metric_data[metric_field.name] = getattr(metric_, metric_field.name)

                    values['metrics'].append(Metric(**metric_data))
            elif protobuf_payload.HasField(field_.name):
                values[field_.name] = getattr(protobuf_payload, field_.name)

        return cls(**values)


    @classmethod
    def from_dict(cls, payload_dict: dict):
        raise NotImplementedError
        if 'metrics' in payload_dict.keys():
            for metric_dict in payload_dict['metrics']:
                pass
        pass



