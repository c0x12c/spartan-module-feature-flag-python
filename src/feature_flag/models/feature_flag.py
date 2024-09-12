from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from feature_flag.core.decorators import table_name


@dataclass
@table_name("feature_flags")
class FeatureFlag:
    name: str
    code: str
    id: Optional[str] = field(default=None, metadata={"exclude_from_db": True})
    description: Optional[str] = None
    enabled: bool = False
    metadata: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = field(
        default=None, metadata={"exclude_from_db": True}
    )
    updated_at: Optional[datetime] = field(
        default=None, metadata={"exclude_from_db": True}
    )
