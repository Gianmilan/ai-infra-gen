from abc import ABC, abstractmethod
from typing import Dict
import logging
import time
import re
from utils.ai_provider import get_ai_provider
from utils.cache import cache
from config.settings import Config

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """Base class for infrastructure generators"""

    def __init__(self):
        self.ai_provider = get_ai_provider()
        self.provider_name = Config.AI_PROVIDER
        logger.info(f"Initialized generator with provider: {self.provider_name}")

    def _clean_response(self, response: str) -> str:
        """Remove markdown code fences and explanatory text from LLM response"""
        # Remove markdown code fences (```hcl, ```yaml, ```)
        cleaned = re.sub(r'^```\w*\n', '', response, flags=re.MULTILINE)
        cleaned = re.sub(r'\n```$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^```$', '', cleaned, flags=re.MULTILINE)

        # Remove leading explanatory text (anything before first valid line)
        # For Terraform: starts with terraform { or provider or variable or resource
        # For Kubernetes: starts with apiVersion or ---
        lines = cleaned.split('\n')
        start_idx = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Check if this looks like the start of valid code
            if (stripped.startswith('terraform {') or
                stripped.startswith('provider ') or
                stripped.startswith('variable ') or
                stripped.startswith('resource ') or
                stripped.startswith('apiVersion:') or
                stripped.startswith('---')):
                start_idx = i
                break

        # Remove trailing explanatory text (anything after last closing brace or last YAML)
        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped and not stripped.startswith('#'):
                # For Terraform: ends with }
                # For YAML: ends with valid YAML line (not explanation)
                if stripped == '}' or ':' in stripped or stripped.startswith('-'):
                    end_idx = i + 1
                    break

        cleaned = '\n'.join(lines[start_idx:end_idx])
        return cleaned.strip()

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
        start_time = time.time()
        logger.info(f"Starting generation for requirements (length: {len(requirements)} chars)")

        # Check cache first
        prompt = self.get_prompt(requirements)
        prompt_hash = hash(prompt + self.provider_name)
        logger.debug(f"Generated prompt hash: {prompt_hash}")

        cached = cache.get(prompt, self.provider_name)

        if cached:
            logger.info(f"Cache hit! Returning cached response (length: {len(cached)} chars)")
            return {
                'code': cached,
                'cached': True,
                'validated': False
            }

        logger.info(f"Cache miss. Generating new code with {self.provider_name}...")

        # Generate new code
        try:
            llm_start = time.time()
            raw_code = self.ai_provider.generate(prompt)
            llm_duration = time.time() - llm_start
            logger.info(f"LLM generation completed in {llm_duration:.2f}s (response length: {len(raw_code)} chars)")

            # Clean up the response (remove markdown, explanations)
            code = self._clean_response(raw_code)
            if code != raw_code:
                logger.info(f"Cleaned response (removed {len(raw_code) - len(code)} chars of markdown/explanations)")
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}", exc_info=True)
            raise

        # Cache the response
        cache.set(prompt, self.provider_name, code)
        logger.debug("Response cached successfully")

        # Validate if enabled
        validated = False
        if Config.ENABLE_VALIDATION:
            logger.info("Validation enabled, starting validation...")
            try:
                val_start = time.time()
                is_valid, errors = self.validate(code)
                val_duration = time.time() - val_start
                validated = is_valid

                if is_valid:
                    logger.info(f"✓ Validation passed in {val_duration:.2f}s")
                else:
                    logger.warning(f"✗ Validation failed in {val_duration:.2f}s")
                    logger.warning(f"Error details: {errors[:500]}")
                    logger.debug(f"Generated code snippet:\n{code[:500]}")

                # Auto-fix if validation failed
                if not is_valid and errors:
                    logger.info("Attempting auto-fix with LLM...")
                    try:
                        fix_start = time.time()
                        code = self.fix_errors(code, errors)
                        fix_duration = time.time() - fix_start
                        logger.info(f"Auto-fix completed in {fix_duration:.2f}s, re-validating...")

                        reval_start = time.time()
                        is_valid, errors = self.validate(code)
                        reval_duration = time.time() - reval_start
                        validated = is_valid

                        if is_valid:
                            logger.info(f"✓ Re-validation passed in {reval_duration:.2f}s")
                        else:
                            logger.error(f"✗ Re-validation failed in {reval_duration:.2f}s: {errors[:200]}")
                    except Exception as e:
                        logger.error(f"Auto-fix failed: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"Validation process failed: {str(e)}", exc_info=True)
        else:
            logger.info("Validation disabled, skipping validation")

        total_duration = time.time() - start_time
        logger.info(f"Generation completed in {total_duration:.2f}s (cached: False, validated: {validated})")

        return {
            'code': code,
            'cached': False,
            'validated': validated
        }

    @abstractmethod
    def fix_errors(self, code: str, errors: str) -> str:
        """Fix validation errors"""
        pass
