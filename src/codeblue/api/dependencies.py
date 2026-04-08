from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from codeblue.persistence.db import get_session

SessionDependency = Annotated[Session, Depends(get_session)]
OptionalTimestampQuery = Annotated[datetime | None, Query()]
