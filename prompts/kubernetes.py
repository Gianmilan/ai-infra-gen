"""
Kubernetes generation prompts
"""

KUBERNETES_GENERATION_PROMPT = """You are an expert Kubernetes engineer. Generate production-ready Kubernetes manifests.

USER REQUIREMENTS:
{requirements}

INSTRUCTIONS:
1. Generate complete, working Kubernetes YAML
2. Include all necessary resources (Deployment, Service, etc.)
3. Add proper resource limits and requests
4. Include health checks (liveness and readiness probes)
5. Use appropriate labels and selectors
6. Follow Kubernetes best practices
7. Add comments explaining key decisions

RESOURCES TO INCLUDE (as needed):
- Deployment: With replicas, rolling update strategy
- Service: ClusterIP, NodePort, or LoadBalancer based on requirements
- ConfigMap: For configuration data
- Secret: For sensitive data (base64 encoded)
- HorizontalPodAutoscaler: If scaling is mentioned
- Ingress: If external access is needed

BEST PRACTICES:
- Set resource requests and limits
- Use readiness and liveness probes
- Implement proper labels and selectors
- Use namespaces for organization
- Security context (runAsNonRoot, readOnlyRootFilesystem)
- Rolling update strategy
- PodDisruptionBudget for HA

STRUCTURE:
Separate each resource with '---'
Order: Namespace → ConfigMap → Secret → Deployment → Service → HPA → Ingress

RETURN ONLY THE YAML. No explanations.
"""

KUBERNETES_FIX_PROMPT = """The following Kubernetes manifests have validation errors. Fix them.

ORIGINAL MANIFESTS:
```yaml
{yaml_content}

VALIDATION ERRORS:
{errors}
Fix all issues and return corrected YAML only.
"""


def get_kubernetes_prompt(requirements: str) -> str:
    """Get formatted Kubernetes generation prompt"""
    return KUBERNETES_GENERATION_PROMPT.format(requirements=requirements)


def get_fix_prompt(yaml_content: str, errors: str) -> str:
    """Get formatted error fix prompt"""
    return KUBERNETES_FIX_PROMPT.format(yaml_content=yaml_content, errors=errors)
