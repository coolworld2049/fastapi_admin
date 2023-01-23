import re
from enum import Enum

from sqlalchemy.dialects import postgresql as ps

instances: dict = {}


class EnumBase(Enum):

    @classmethod
    def as_snake_case(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', str(cls.__name__)).lower()

    @classmethod
    def col_name(cls):
        return cls.as_snake_case().split('_')[-1]

    @classmethod
    def to_list(cls) -> list:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def to_dict(cls) -> dict:
        return {cls.as_snake_case(): {c.name: c.value for c in cls}}


class UserRole(EnumBase):
    admin = 'admin'
    anon = 'anon'


class TaskStatus(EnumBase):
    unassigned = 'unassigned'
    pending = 'pending'
    started = 'started'
    verifying = 'verifying'
    accepted = 'accepted'
    overdue = 'overdue'
    completed = 'completed'


class TaskPriority(EnumBase):
    high = 'high'
    medium = 'medium'
    low = 'low'


pg_custom_type_colnames = [
    UserRole.col_name(),
    TaskStatus.col_name(),
    TaskPriority.col_name(),
]

user_role = ps.ENUM(*UserRole.to_list(), name=UserRole.as_snake_case())
task_status = ps.ENUM(*TaskStatus.to_list(), name=TaskStatus.as_snake_case())
task_priority = ps.ENUM(*TaskPriority.to_list(), name=TaskPriority.as_snake_case())

instances.update(UserRole.to_dict())
instances.update(TaskStatus.to_dict())
instances.update(TaskPriority.to_dict())
