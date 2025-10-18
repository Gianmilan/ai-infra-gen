import os
import subprocess
import tempfile
import logging
import re
from pathlib import Path
from generators.base import BaseGenerator
from prompts.terraform import get_terraform_prompt, get_fix_prompt

logger = logging.getLogger(__name__)


class TerraformGenerator(BaseGenerator):
    """Terraform infrastructure generator"""

    def get_prompt(self, requirements: str) -> str:
        return get_terraform_prompt(requirements)

    def _clean_response(self, response: str) -> str:
        """Clean Terraform-specific issues"""
        # First apply base cleanup
        cleaned = super()._clean_response(response)

        # Fix common Terraform issues from LLMs
        # 1. Replace // comments with # comments
        lines = []
        for line in cleaned.split('\n'):
            # Replace // with # but preserve URLs like https://
            if '//' in line and 'https://' not in line and 'http://' not in line:
                # Only replace // at start of comment (with optional whitespace)
                line = re.sub(r'(\s+)//\s*', r'\1# ', line)
            lines.append(line)
        cleaned = '\n'.join(lines)

        # 2. Fix missing quotes around provider names
        # provider aws { -> provider "aws" {
        cleaned = re.sub(r'provider\s+(\w+)\s*{', r'provider "\1" {', cleaned)

        # 3. Fix resource syntax
        # resource aws_s3_bucket name { -> resource "aws_s3_bucket" "name" {
        cleaned = re.sub(r'resource\s+(\w+)\s+(\w+)\s*{', r'resource "\1" "\2" {', cleaned)

        logger.debug("Applied Terraform-specific cleanup")
        return cleaned

    def validate(self, code: str) -> tuple[bool, str]:
        """Validate Terraform code"""
        logger.info("Starting Terraform validation")

        # Check if terraform is installed
        if os.system('which terraform > /dev/null 2>&1') != 0:
            logger.error("Terraform CLI not found in PATH")
            return False, "Terraform not installed"

        logger.debug("Terraform CLI found, proceeding with validation")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                logger.debug(f"Created temporary directory: {tmpdir}")

                # Write code to file
                tf_file = Path(tmpdir) / 'main.tf'
                tf_file.write_text(code)
                logger.debug(f"Wrote {len(code)} chars to {tf_file}")

                # Run terraform init
                logger.info("Running terraform init...")
                init_result = subprocess.run(
                    ['terraform', 'init', '-backend=false'],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=30
                )

                if init_result.returncode != 0:
                    stderr = init_result.stderr.decode()
                    stdout = init_result.stdout.decode()
                    logger.error(f"terraform init failed (exit {init_result.returncode})")
                    logger.error(f"STDERR: {stderr}")
                    logger.error(f"STDOUT: {stdout}")
                    logger.error(f"Generated code that failed:\n{code[:1000]}")
                    return False, stderr

                logger.info("terraform init succeeded")

                # Run terraform validate
                logger.info("Running terraform validate...")
                validate_result = subprocess.run(
                    ['terraform', 'validate'],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=30
                )

                if validate_result.returncode != 0:
                    stderr = validate_result.stderr.decode()
                    logger.error(f"terraform validate failed (exit {validate_result.returncode}): {stderr[:500]}")
                    return False, stderr

                logger.info("terraform validate succeeded")
                return True, ""

        except subprocess.TimeoutExpired as e:
            logger.error(f"Terraform validation timed out after 30s: {e}")
            return False, "Validation timed out"
        except Exception as e:
            logger.error(f"Terraform validation exception: {str(e)}", exc_info=True)
            return False, str(e)

    def fix_errors(self, code: str, errors: str) -> str:
        """Fix Terraform validation errors"""
        logger.info(f"Attempting to fix Terraform errors (error length: {len(errors)} chars)")
        prompt = get_fix_prompt(code, errors)
        logger.debug(f"Generated fix prompt (length: {len(prompt)} chars)")
        fixed_code = self.ai_provider.generate(prompt)
        logger.info(f"Received fixed code from LLM (length: {len(fixed_code)} chars)")
        return fixed_code