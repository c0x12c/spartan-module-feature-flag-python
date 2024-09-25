from enum import Enum


class ChangeStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    UPDATED = "updated"
    DELETED = "deleted"
