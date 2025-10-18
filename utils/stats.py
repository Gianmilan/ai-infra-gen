"""
Usage statistics tracking
"""
import json
from datetime import datetime
from config.settings import Config


def track_generation(infra_type: str):
    """Track a generation event"""
    stats_file = Config.STATS_FILE

    # Load existing stats
    if stats_file.exists():
        stats = json.loads(stats_file.read_text())
    else:
        stats = {
            'total': 0,
            'terraform': 0,
            'kubernetes': 0,
            'first_used': None,
            'last_used': None
        }

    # Update stats
    stats['total'] += 1
    stats[infra_type] = stats.get(infra_type, 0) + 1

    if not stats['first_used']:
        stats['first_used'] = int(datetime.now().timestamp())
    stats['last_used'] = int(datetime.now().timestamp())

    # Save
    stats_file.write_text(json.dumps(stats, indent=2))


def get_stats() -> dict:
    """Get current statistics"""
    stats_file = Config.STATS_FILE

    if stats_file.exists():
        return json.loads(stats_file.read_text())

    return {
        'total': 0,
        'terraform': 0,
        'kubernetes': 0
    }


def reset_stats():
    """Reset all statistics"""
    Config.STATS_FILE.write_text(json.dumps({
        'total': 0,
        'terraform': 0,
        'kubernetes': 0
    }, indent=2))