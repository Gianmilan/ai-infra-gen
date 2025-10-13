from abc import ABC, abstractmethod
from typing import Dict
from utils.ai_provider import get_ai_provider
from utils.cache import cache
from config.settings import Config


class BaseGenerator(ABC):
    """Base class for infrastructure generators"""

    def __init__(self):
        self.ai_provider = get_ai_provider()
        self.provider_name = Config.AI_PROVIDER

    @abstractmethod
    def get_prompt(self, requirements: str) -> str:
        """Get generation prompt"""
        pass

    @abstractmethod
    def validate(self, code: str) -> tuple[bool, str]:
        """Validate generated code"""
        pass

    def generate(self, requirements: str) -> Dict:
        """Generate infrastructure code"""

        # Check cache first
        prompt = self.get_prompt(requirements)
        cached = cache.get(prompt, self.provider_name)

        if cached:
            return {
                'code': cached,
                'cached': True,
                'validated': False
            }

        # Generate new code
        print(f"Generating with {self.provider_name}...")
        code = self.ai_provider.generate(prompt)

        # Cache the response
        cache.set(prompt, self.provider_name, code)

        # Validate if enabled
        validated = False
        if Config.ENABLE_VALIDATION:
            is_valid, errors = self.validate(code)
            validated = is_valid

            # Auto-fix if validation failed
            if not is_valid and errors:
                print("Validation failed, attempting auto-fix...")
                code = self.fix_errors(code, errors)
                is_valid, errors = self.validate(code)
                validated = is_valid

        return {
            'code': code,
            'cached': False,
            'validated': validated
        }

    @abstractmethod
    def fix_errors(self, code: str, errors: str) -> str:
        """Fix validation errors"""
        pass
