"""SQLAlchemy models for the acquisition platform.

Import all model modules here so that `Base.metadata` is complete when
callers do `from app.models.base import Base` and then
`Base.metadata.create_all(engine)`.
"""
from app.models.base import Base  # noqa: F401
from app.models import source  # noqa: F401
from app.models import datapoint  # noqa: F401
from app.models import property_ as property_models  # noqa: F401
from app.models import listing  # noqa: F401
from app.models import market  # noqa: F401
from app.models import valuation  # noqa: F401
from app.models import audit  # noqa: F401
from app.models import stubs  # noqa: F401
