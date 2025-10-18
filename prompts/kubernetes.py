"""
Kubernetes generation prompts
"""

KUBERNETES_GENERATION_PROMPT = """Generate Kubernetes YAML based on requirements. Output ONLY valid YAML.

REQUIREMENTS: {requirements}

Generate complete manifests with:
1. ALL resources needed (Namespace, Deployment, Service, ConfigMap, etc.)
2. Proper labels (selector.matchLabels MUST match template.metadata.labels)
3. Resource requests/limits
4. Liveness/readiness probes
5. Security settings (runAsNonRoot, readOnlyRootFilesystem)

Rules:
- Separate resources with ---
- No markdown fences, no explanatory text
- Start with apiVersion: and end with last resource
- Brief comments allowed for clarity

Example start:
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: nginx
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80

# Now generate all resources for: {requirements}"""

KUBERNETES_FIX_PROMPT = """Fix the validation errors in this Kubernetes YAML. Output ONLY the corrected YAML.

BROKEN YAML:
{yaml_content}

ERRORS:
{errors}

CRITICAL:
- Fix label mismatches (selector.matchLabels must match template.metadata.labels exactly)
- Fix indentation
- NO markdown, NO backticks, NO explanations
- Start with apiVersion: and end with last resource

Output only the corrected YAML, nothing else."""


def get_kubernetes_prompt(requirements: str) -> str:
    """Get formatted Kubernetes generation prompt"""
    return KUBERNETES_GENERATION_PROMPT.format(requirements=requirements)


def get_fix_prompt(yaml_content: str, errors: str) -> str:
    """Get formatted error fix prompt"""
    return KUBERNETES_FIX_PROMPT.format(yaml_content=yaml_content, errors=errors)
