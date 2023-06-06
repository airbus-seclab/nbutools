import enum


class ScanState(enum.Enum):
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    SKIPPED = 3
    ERROR = -1


class NbuComponentType(enum.Enum):
    OPSCENTER = "OpsCenter"
    PRIMARY = "Primary Server"
    MEDIA = "Media Server"
    CLIENT = "Client"
    UNKNOWN = "Unknown"
