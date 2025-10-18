"""
Terraform generation prompts
"""

TERRAFORM_GENERATION_PROMPT = """Generate Terraform code for AWS Provider 5.x. Output ONLY valid HCL.

REQUIREMENTS: {requirements}

IMPORTANT - AWS Provider 5.x changes:
- S3: Use separate resources (aws_s3_bucket, aws_s3_bucket_versioning, aws_s3_bucket_lifecycle_configuration)
- S3: Do NOT use inline versioning/lifecycle blocks
- Security Groups: Use aws_security_group + aws_vpc_security_group_*_rule resources

Generate complete code with:
1. terraform/provider blocks (AWS ~> 5.0)
2. variables with sensible defaults
3. ALL resources needed for requirements
4. outputs for important values

Rules:
- Use double quotes "..." only
- Start with terraform {{ and end with }}
- No markdown, no explanations
- Brief # comments allowed
- Do NOT use "```", use "heredoc" syntax "<<EOT"
- Variables are not allowed in varible "bucket_name"

Example:
terraform {{
  required_providers {{
    aws = {{ source = "hashicorp/aws", version = "~> 5.0" }}
  }}
}}

provider "aws" {{ region = var.region }}
variable "region" {{ default = "us-east-1" }}

# Generate resources for: {requirements}"""

TERRAFORM_FIX_PROMPT = """Fix the validation errors in this Terraform code. Output ONLY the corrected HCL.

BROKEN CODE:
{code}

ERRORS:
{errors}

CRITICAL:
- Use double quotes "..." not single quotes '
- Use # for comments not //
- NO backticks, NO explanations, NO markdown
- Start with terraform {{ and end with the last }}

Output only the corrected code, nothing else."""


def get_terraform_prompt(requirements: str) -> str:
    """Get formatted Terraform generation prompt"""
    return TERRAFORM_GENERATION_PROMPT.format(requirements=requirements)


def get_fix_prompt(code: str, errors: str) -> str:
    """Get formatted error fix prompt"""
    return TERRAFORM_FIX_PROMPT.format(code=code, errors=errors)
