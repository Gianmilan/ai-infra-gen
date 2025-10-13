"""
Terraform generation prompts
"""

TERRAFORM_GENERATION_PROMPT = """You are an expert DevOps engineer. Generate production-ready Terraform code for AWS.

USER REQUIREMENTS:
{requirements}

INSTRUCTIONS:
1. Generate complete, working Terraform code
2. Use variables for all configurable values
3. Include proper resource naming with project/environment tags
4. Follow AWS best practices for security
5. Add helpful comments explaining key decisions
6. Include outputs for important values
7. Use appropriate resource types and configurations
8. Ensure high availability where needed

STRUCTURE YOUR CODE:
- Start with terraform block and required providers
- Then variables (with descriptions and defaults)
- Then resources (logical grouping)
- End with outputs

SECURITY BEST PRACTICES:
- Use private subnets for databases and app servers
- Implement least-privilege security groups
- Enable encryption at rest and in transit
- Use IMDSv2 for EC2 instances
- Enable VPC flow logs
- Use Secrets Manager for sensitive data (not hardcoded)

HIGH AVAILABILITY:
- Multi-AZ deployments where appropriate
- Auto Scaling Groups for compute
- RDS Multi-AZ for databases
- Cross-zone load balancing

RETURN ONLY THE TERRAFORM CODE. No explanations before or after.
"""

TERRAFORM_FIX_PROMPT = """The following Terraform code has validation errors. Fix them while maintaining the original intent.

ORIGINAL CODE:
```hcl
{code}

VALIDATION ERRORS:
{errors}
INSTRUCTIONS:

Analyze each error carefully
Fix syntax issues
Resolve missing dependencies
Correct resource references
Maintain the original functionality

RETURN ONLY THE CORRECTED TERRAFORM CODE. No explanations."""


def get_terraform_prompt(requirements: str) -> str:
    """Get formatted Terraform generation prompt"""
    return TERRAFORM_GENERATION_PROMPT.format(requirements=requirements)


def get_fix_prompt(code: str, errors: str) -> str:
    """Get formatted error fix prompt"""
    return TERRAFORM_FIX_PROMPT.format(code=code, errors=errors)
