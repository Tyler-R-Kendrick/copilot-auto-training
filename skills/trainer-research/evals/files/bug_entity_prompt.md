Extract structured bug-report fields from the issue text.

Issue text:
{issue_text}

Return JSON with this schema:
{
  "product": "string|null",
  "version": "string|null",
  "platform": "string|null",
  "error_code": "string|null",
  "severity": "critical|high|medium|low|null",
  "missing_fields": ["string"]
}