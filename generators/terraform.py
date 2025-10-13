import os
import subprocess
import tempfile
from pathlib import Path
from generators.base import BaseGenerator
from prompts.terraform import get_terraform_prompt, get_fix_prompt


class TerraformGenerator(BaseGenerator):
    """Terraform infrastructure generator"""

    def get_prompt(self, requirements: str) -> str:
        return get_terraform_prompt(requirements)

    def validate(self, code: str) -> tuple[bool, str]:
        """Validate Terraform code"""

        # Check if terraform is installed
        if os.system('which terraform > /dev/null 2>&1') != 0:
            return False, "Terraform not installed"

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write code to file
                tf_file = Path(tmpdir) / 'main.tf'
                tf_file.write_text(code)

                # Run terraform init
                init_result = subprocess.run(
                    ['terraform', 'init', '-backend=false'],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=30
                )

                if init_result.returncode != 0:
                    return False, init_result.stderr.decode()

                # Run terraform validate
                validate_result = subprocess.run(
                    ['terraform', 'validate'],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=30
                )

                if validate_result.returncode != 0:
                    return False, validate_result.stderr.decode()

                return True, ""

        except subprocess.TimeoutExpired:
            return False, "Validation timed out"
        except Exception as e:
            return False, str(e)

    def fix_errors(self, code: str, errors: str) -> str:
        """Fix Terraform validation errors"""
        prompt = get_fix_prompt(code, errors)
        return self.ai_provider.generate(prompt)