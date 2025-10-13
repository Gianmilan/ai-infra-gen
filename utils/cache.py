import json
import hashlib
from pathlib import Path
from typing import Optional
from config.settings import Config


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

    def _get_key(self, prompt: str, provider: str) -> str:
        """Generate cache key from prompt and provider"""
        content = f"{provider}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, provider: str) -> Optional[str]:
        """Get cached response"""
        if not self.enabled:
            return None

        key = self._get_key(prompt, provider)
        cache = json.loads(self.cache_file.read_text())

        if key in cache:
            print(f"✓ Cache hit for {provider}")
            return cache[key]

        return None

    def set(self, prompt: str, provider: str, response: str):
        """Cache a response"""
        if not self.enabled:
            return

        key = self._get_key(prompt, provider)
        cache = json.loads(self.cache_file.read_text())
        cache[key] = response

        self.cache_file.write_text(json.dumps(cache, indent=2))
        print(f"✓ Cached response for {provider}")

    def clear(self):
        """Clear all cached responses"""
        self.cache_file.write_text('{}')
        print("✓ Cache cleared")

    def size(self) -> int:
        """Get number of cached items"""
        cache = json.loads(self.cache_file.read_text())
        return len(cache)


# Global cache instance
cache = ResponseCache()