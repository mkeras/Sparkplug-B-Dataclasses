class SparkplugBError(Exception):
    pass


class IllegalTopicCharError(SparkplugBError):
    pass


class OutOfSpecError(SparkplugBError):
    pass
