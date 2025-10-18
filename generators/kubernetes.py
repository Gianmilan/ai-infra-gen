import os
import subprocess
import tempfile
import logging
from generators.base import BaseGenerator
from prompts.kubernetes import get_kubernetes_prompt, get_fix_prompt

logger = logging.getLogger(__name__)


class KubernetesGenerator(BaseGenerator):
    """Kubernetes manifest generator"""

    def get_prompt(self, requirements: str) -> str:
        return get_kubernetes_prompt(requirements)

    def validate(self, yaml_content: str) -> tuple[bool, str]:
        """Validate Kubernetes YAML"""
        logger.info("Starting Kubernetes validation")

        # Check if kubectl is installed
        if os.system('which kubectl > /dev/null 2>&1') != 0:
            logger.error("kubectl CLI not found in PATH")
            return False, "kubectl not installed"

        logger.debug("kubectl CLI found, proceeding with validation")

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_content)
                f.flush()
                logger.debug(f"Wrote {len(yaml_content)} chars to temporary file: {f.name}")

                # Run kubectl dry-run
                logger.info("Running kubectl apply --dry-run=client...")
                result = subprocess.run(
                    ['kubectl', 'apply', '--dry-run=client', '-f', f.name],
                    capture_output=True,
                    timeout=10
                )

                os.unlink(f.name)
                logger.debug(f"Cleaned up temporary file: {f.name}")

                if result.returncode != 0:
                    stderr = result.stderr.decode()
                    logger.error(f"kubectl validation failed (exit {result.returncode}): {stderr[:500]}")
                    return False, stderr

                stdout = result.stdout.decode()
                logger.info(f"kubectl validation succeeded: {stdout[:200]}")
                return True, ""

        except subprocess.TimeoutExpired as e:
            logger.error(f"Kubernetes validation timed out after 10s: {e}")
            return False, "Validation timed out"
        except Exception as e:
            logger.error(f"Kubernetes validation exception: {str(e)}", exc_info=True)
            return False, str(e)

    def fix_errors(self, yaml_content: str, errors: str) -> str:
        """Fix Kubernetes validation errors"""
        logger.info(f"Attempting to fix Kubernetes errors (error length: {len(errors)} chars)")
        prompt = get_fix_prompt(yaml_content, errors)
        logger.debug(f"Generated fix prompt (length: {len(prompt)} chars)")
        fixed_yaml = self.ai_provider.generate(prompt)
        logger.info(f"Received fixed YAML from LLM (length: {len(fixed_yaml)} chars)")
        return fixed_yaml
