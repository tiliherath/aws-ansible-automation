# AWS Ansible Automation

Automated Linux server health monitoring and reporting using **Ansible, AWS Systems Manager (SSM), GitHub Actions, AWS IAM, and Amazon Linux 2023**.

The project demonstrates how Ansible can be integrated with AWS infrastructure and a GitHub Actions CI/CD workflow to remotely manage EC2 instances, collect system health information, generate structured reports, store workflow artifacts, and send reports by email.

---

## Architecture

```text
                    GitHub Repository
                           |
                           v
                  GitHub Actions Workflow
                           |
                           | OIDC
                           v
                    AWS IAM Role
                           |
                           v
                  AWS Systems Manager
                       (SSM)
                    /          \
                   /            \
                  v              v
          Amazon Linux 2023  Amazon Linux 2023
              web01              web02
                 \                /
                  \              /
                   \            /
                    Health Checks
                           |
                           v
                    Ansible Facts
                           |
                           v
                 JSON / HTML Reports
                           |
              +------------+------------+
              |                         |
              v                         v
       GitHub Actions Artifact      SMTP Email
                                  HTML + JSON
```

---

## Project Objectives

* Automate Linux server health checks using Ansible.
* Manage AWS EC2 instances through AWS Systems Manager.
* Avoid direct SSH connectivity from GitHub Actions.
* Authenticate GitHub Actions to AWS using OIDC.
* Collect Linux system information automatically.
* Check root filesystem utilization.
* Verify SSH service status.
* Generate JSON and HTML health reports.
* Store reports as GitHub Actions artifacts.
* Send health reports through SMTP email.
* Demonstrate infrastructure automation using a repeatable workflow.

---

## Technologies Used

| Technology          | Purpose                                  |
| ------------------- | ---------------------------------------- |
| AWS EC2             | Linux server infrastructure              |
| Amazon Linux 2023   | Target operating system                  |
| AWS Systems Manager | Remote server connectivity               |
| AWS IAM             | Access control and GitHub OIDC role      |
| Ansible             | Configuration management and automation  |
| Jinja2              | Report templating                        |
| GitHub Actions      | Workflow automation                      |
| GitHub OIDC         | Keyless AWS authentication               |
| Python              | Email reporting script                   |
| SMTP / Gmail        | Report delivery                          |
| YAML                | Ansible and GitHub Actions configuration |
| JSON / HTML         | Health report formats                    |

---

## AWS Environment

The project uses two Amazon Linux 2023 EC2 instances:

```text
web01
web02
```

The servers are accessed through **AWS Systems Manager (SSM)** rather than traditional SSH connections.

AWS Region:

```text
us-east-1
```

---

## Repository Structure

```text
aws-ansible-automation/
│
├── .github/
│   └── workflows/
│       └── ansible-deploy.yml
│
├── ansible/
│   ├── group_vars/
│   │
│   ├── inventory/
│   │   └── hosts.yml
│   │
│   ├── playbooks/
│   │   ├── health_check.yml
│   │   └── templates/
│   │       ├── health_report.html.j2
│   │       └── health_report.json.j2
│   │
│   ├── roles/
│   │
│   └── templates/
│
├── reports/
│   ├── html/
│   └── json/
│
├── scripts/
│   └── send_health_report.py
│
├── ansible.cfg
│
└── README.md
```

---

# Ansible Automation

The main playbook is:

```text
ansible/playbooks/health_check.yml
```

The playbook performs health checks against all target servers.

### Information collected

* Hostname
* Operating system
* OS version
* Kernel version
* System uptime
* CPU cores
* Total memory
* Root filesystem
* Disk utilization
* SSH service status

Ansible gathers system information using Ansible facts and performs additional Linux commands where required.

---

## Root Filesystem Check

The automation checks the root filesystem using:

```bash
df -h
```

The result is parsed into structured information including:

```text
Device
Size
Used
Available
Usage %
Mount point
```

This information is included in the generated health reports.

---

## SSH Service Check

The playbook verifies the Linux SSH service using Ansible's systemd module.

```yaml
ansible.builtin.systemd:
  name: sshd
```

The service state is included in the health report.

---

# AWS Systems Manager Integration

The project uses the Ansible AWS SSM connection instead of requiring direct SSH access from GitHub Actions.

Conceptually:

```text
GitHub Actions
      |
      v
AWS IAM
      |
      v
AWS SSM
      |
      +----> web01
      |
      +----> web02
```

This provides a useful alternative to exposing SSH access to the automation environment.

---

# GitHub Actions Automation

The workflow is located at:

```text
.github/workflows/ansible-deploy.yml
```

The workflow can be started manually using:

```yaml
on:
  workflow_dispatch:
```

The workflow performs the following major steps:

```text
Checkout repository
        ↓
Set up Python
        ↓
Install Ansible
        ↓
Install AWS dependencies
        ↓
Configure AWS credentials
        ↓
Verify AWS identity
        ↓
Verify repository/workspace
        ↓
Run Ansible health check
        ↓
Generate reports
        ↓
Upload reports as artifact
        ↓
Send report by email
```

---

# GitHub OIDC Authentication

The workflow uses **GitHub Actions OpenID Connect (OIDC)** to authenticate to AWS.

The workflow grants:

```yaml
permissions:
  id-token: write
  contents: read
```

AWS credentials are configured using:

```yaml
aws-actions/configure-aws-credentials
```

The IAM role is supplied through the GitHub repository secret:

```text
AWS_ROLE_TO_ASSUME
```

The workflow verifies the authenticated AWS identity using:

```bash
aws sts get-caller-identity
```

### Why OIDC?

OIDC avoids storing a long-lived AWS access key and secret key in GitHub repository secrets.

The authentication flow is:

```text
GitHub Actions
      |
      | OIDC token
      v
AWS IAM
      |
      | AssumeRole
      v
Temporary AWS credentials
      |
      v
AWS resources
```

---

# Health Report Generation

Two report formats are generated using Jinja2 templates.

### JSON

```text
reports/json/health_report.json
```

### HTML

```text
reports/html/health_report.html
```

Templates are stored under:

```text
ansible/playbooks/templates/
```

The playbook uses Ansible's `template` module to generate the reports.

---

# GitHub Actions Artifacts

Because GitHub-hosted runners are temporary, generated reports would normally disappear when the workflow finishes.

The workflow therefore uploads the reports using:

```yaml
actions/upload-artifact
```

Artifact name:

```text
aws-health-reports
```

The artifact contains the generated health reports.

---

# Email Reporting

The project also sends the health report through SMTP.

The Python script is:

```text
scripts/send_health_report.py
```

The script:

1. Reads SMTP configuration from environment variables.
2. Verifies that the reports exist.
3. Loads the HTML report.
4. Uses the HTML report as the email body.
5. Attaches the JSON report.
6. Connects to the SMTP server using TLS.
7. Authenticates.
8. Sends the email.

The following values are stored as GitHub repository secrets:

```text
SMTP_SERVER
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
REPORT_EMAIL_TO
```

No SMTP credentials are stored in the source code.

---

# Successful Validation

The complete Ansible workflow was successfully executed against both Linux servers.

Example play recap:

```text
PLAY RECAP

localhost : ok=4  changed=3  unreachable=0  failed=0
web01     : ok=15 changed=0  unreachable=0  failed=0
web02     : ok=15 changed=0  unreachable=0  failed=0
```

The workflow successfully:

* Connected to both EC2 instances through SSM.
* Gathered Linux system facts.
* Performed filesystem checks.
* Checked SSH service status.
* Generated JSON reports.
* Generated HTML reports.
* Uploaded the reports as a GitHub Actions artifact.
* Sent the health report through SMTP email.

---

# Security Considerations

The project follows several security-focused practices:

* GitHub Actions authenticates to AWS using OIDC.
* Long-lived AWS credentials are not required by the GitHub workflow.
* SMTP credentials are stored in GitHub Secrets.
* Ansible communicates with EC2 through AWS Systems Manager.
* Sensitive credentials are excluded from the repository.
* AWS IAM is used to control permissions.
* The workflow uses read-only repository permissions where appropriate.

---

# Key Skills Demonstrated

### Linux

* Amazon Linux administration
* Filesystem monitoring
* Systemd service management
* Linux system information
* SSH service management
* Troubleshooting

### Ansible

* Inventory management
* Ansible facts
* Playbooks
* Tasks
* Modules
* Variables and facts
* Jinja2 templates
* Registered variables
* Structured report generation
* AWS SSM connectivity

### AWS

* EC2
* Systems Manager
* IAM
* OIDC
* STS
* AWS authentication
* Cloud infrastructure automation

### DevOps / Automation

* GitHub Actions
* CI/CD workflow design
* Secrets management
* Artifact management
* Automated reporting
* SMTP integration
* Python scripting

---

# What I Learned

This project provided practical experience integrating several technologies into a single automation workflow:

```text
Linux
  +
Ansible
  +
AWS SSM
  +
AWS IAM
  +
GitHub OIDC
  +
GitHub Actions
  +
Jinja2
  +
Python
  +
SMTP
```

A key lesson was understanding that automation running on a temporary GitHub-hosted runner requires explicit handling of generated files. Uploading the reports as workflow artifacts ensures that the results remain accessible after the workflow completes.

The project also provided practical experience troubleshooting Ansible paths, AWS authentication, SSM connectivity, report generation, and SMTP delivery.

---

# Future Improvements

Possible future enhancements include:

* Ansible linting in GitHub Actions
* Ansible syntax validation
* Automated testing
* Additional Linux health metrics
* CPU and memory threshold alerts
* Disk-space threshold alerts
* Multiple environment support
* Ansible roles for reusable automation
* Scheduled health checks

These enhancements are intentionally outside the current completed scope of the project.

---

# Project Status

**Completed**

The project successfully demonstrates an end-to-end AWS Linux automation workflow using Ansible and GitHub Actions.

```text
AWS Infrastructure
        ↓
AWS SSM
        ↓
Ansible Automation
        ↓
Linux Health Checks
        ↓
JSON + HTML Reports
        ↓
GitHub Artifact
        ↓
Email Notification
```

---

## Author

**Thilini Amarasinghe**

Systems / Linux / Cloud Infrastructure Engineer

Core interests:

* Linux Infrastructure
* AWS Cloud
* Ansible Automation
* Systems Engineering
* Cloud Infrastructure
* DevOps Automation
