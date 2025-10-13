import os
import subprocess
import tempfile
from generators.base import BaseGenerator
from prompts.kubernetes import get_kubernetes_prompt, get_fix_prompt


class KubernetesGenerator(BaseGenerator):
    """Kubernetes manifest generator"""

    def get_prompt(self, requirements: str) -> str:
        return get_kubernetes_prompt(requirements)

    def validate(self, yaml_content: str) -> tuple[bool, str]:
        """Validate Kubernetes YAML"""

        # Check if kubectl is installed
        if os.system('which kubectl > /dev/null 2>&1') != 0:
            return False, "kubectl not installed"

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_content)
                f.flush()

                # Run kubectl dry-run
                result = subprocess.run(
                    ['kubectl', 'apply', '--dry-run=client', '-f', f.name],
                    capture_output=True,
                    timeout=10
                )

                os.unlink(f.name)

                if result.returncode != 0:
                    return False, result.stderr.decode()

                return True, ""

        except subprocess.TimeoutExpired:
            return False, "Validation timed out"
        except Exception as e:
            return False, str(e)

    def fix_errors(self, yaml_content: str, errors: str) -> str:
        """Fix Kubernetes validation errors"""
        prompt = get_fix_prompt(yaml_content, errors)
        return self.ai_provider.generate(prompt)
