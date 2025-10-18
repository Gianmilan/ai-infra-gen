import json
import hashlib
import logging
from typing import Optional, Dict
from config.settings import Config

logger = logging.getLogger(__name__)


def _get_key(prompt: str, provider: str) -> str:
    """Generate cache key from prompt and provider"""
    content = f"{provider}:{prompt}"
    return hashlib.md5(content.encode()).hexdigest()


class ResponseCache:
    """Simple file-based cache for AI responses"""

    def __init__(self):
        self.cache_file = Config.CACHE_FILE
        self.enabled = Config.ENABLE_CACHE
        self._ensure_cache_exists()

    def _ensure_cache_exists(self):
        """Create cache file if it doesn't exist"""
        if not self.cache_file.exists():
            self.cache_file.write_text('{}')

    def get(self, prompt: str, provider: str) -> Optional[str]:
        """Get cached response"""
        if not self.enabled:
            return None

        key = _get_key(prompt, provider)
        cache = json.loads(self.cache_file.read_text())

        if key in cache:
            logger.info(f"Cache hit for {provider} (key: {key[:8]}...)")
            return cache[key]

        logger.debug(f"Cache miss for {provider} (key: {key[:8]}...)")
        return None

    def set(self, prompt: str, provider: str, response: str):
        """Cache a response"""
        if not self.enabled:
            return

        key = _get_key(prompt, provider)
        cache = json.loads(self.cache_file.read_text())
        cache[key] = response

        self.cache_file.write_text(json.dumps(cache, indent=2))
        logger.info(f"Cached response for {provider} (key: {key[:8]}..., size: {len(response)} chars)")

    def clear(self):
        """Clear all cached responses"""
        count = self.size()
        self.cache_file.write_text('{}')
        logger.info(f"Cache cleared ({count} items removed)")
        return count

    def size(self) -> int:
        """Get number of cached items"""
        cache = json.loads(self.cache_file.read_text())
        return len(cache)

    def info(self) -> Dict:
        """Get cache information"""
        cache = json.loads(self.cache_file.read_text())
        total_size = sum(len(v) for v in cache.values())

        return {
            'enabled': self.enabled,
            'items': len(cache),
            'total_chars': total_size,
            'total_bytes': self.cache_file.stat().st_size if self.cache_file.exists() else 0,
            'file_path': str(self.cache_file)
        }


# Global cache instance
cache = ResponseCache()