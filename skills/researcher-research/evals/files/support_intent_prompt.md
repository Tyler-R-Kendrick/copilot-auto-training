Classify the support ticket into one of these labels: billing, bug, access, cancellation.

Ticket:
{ticket_text}

Return JSON with this schema:
{
  "label": "billing|bug|access|cancellation",
  "confidence": 0.0,
  "rationale": "short explanation"
}