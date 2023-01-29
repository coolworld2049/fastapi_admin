# Import all the models, so that Base has them before being
# imported by Alembic

from app.models import *
from app.db.session import Base
