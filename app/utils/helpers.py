import datetime
import json
from typing import Any

def format_date(dt: Any) -> str:
    """Formats datetime objects to standard human-readable string."""
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%b %d, %Y %I:%M %p")
    return str(dt)

def get_score_color(score: float) -> str:
    """Returns color hex/name based on the score threshold for badges."""
    if score >= 80:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling datetime objects."""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)
