# The Lethal Trifecta

Based on Simon Willison's concept of the "lethal trifecta" — three capabilities that, when co-located in a single component, create a disproportionately dangerous attack surface.

## The Three Legs

1. **Private data access** — Reading from databases, credential stores, environment secrets, PII fields
2. **Untrusted input processing** — Handling request parameters, form data, webhook payloads, file uploads, deserialized data
3. **External communication** — Making outbound HTTP requests, sending emails, publishing to queues, dispatching webhooks

## Why Co-Occurrence Is Dangerous

Any single leg is normal. Two legs together require careful handling. All three in one file/function create a direct path for:

- **Data exfiltration via SSRF**: Untrusted input controls a URL → handler reads credentials → outbound request leaks them
- **Prompt injection escalation**: AI tool receives untrusted input → accesses internal state → calls external API with attacker-controlled payload
- **SQL injection + notification**: User input → database query → result sent via email/webhook (error-based exfiltration)

The key insight: an attacker only needs to compromise the untrusted-input leg to weaponize the other two.

## Anti-Pattern Example

```python
# BAD: All three legs in one handler
@app.route("/api/process-webhook", methods=["POST"])
def process_webhook():
    # Leg 2: Untrusted input
    payload = request.json

    # Leg 1: Private data access
    user = db.query("SELECT * FROM users WHERE id = %s", (payload["user_id"],))
    api_key = os.environ["INTERNAL_API_KEY"]

    # Leg 3: External communication
    requests.post(
        payload["callback_url"],  # Attacker-controlled destination!
        json={"user": user, "key": api_key},
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return jsonify({"status": "ok"})
```

## Remediation Patterns

### 1. Separation of Concerns

Split each leg into its own module with a narrow interface:

```python
# input_handler.py — Leg 2 only
def validate_webhook(payload: dict) -> WebhookRequest:
    """Validate and sanitize untrusted input. No DB access, no outbound calls."""
    return WebhookRequest(
        user_id=validate_uuid(payload["user_id"]),
        action=validate_enum(payload["action"], ALLOWED_ACTIONS),
    )

# data_layer.py — Leg 1 only
def get_user_for_notification(user_id: str) -> NotificationPayload:
    """Read user data. No request parsing, no external calls."""
    user = db.query("SELECT name, email FROM users WHERE id = %s", (user_id,))
    return NotificationPayload(name=user.name, email=user.email)

# notifier.py — Leg 3 only (with allowlist)
ALLOWED_CALLBACK_HOSTS = {"hooks.slack.com", "api.pagerduty.com"}

def send_notification(payload: NotificationPayload, destination: str):
    """Send to pre-approved destinations only. No input parsing, no DB access."""
    host = urlparse(destination).hostname
    if host not in ALLOWED_CALLBACK_HOSTS:
        raise ValueError(f"Blocked callback host: {host}")
    requests.post(destination, json=asdict(payload))
```

### 2. Principle of Least Privilege

- Input handlers should not have database credentials
- Data access layers should not have outbound network access
- Notification services should use allowlisted destinations only

### 3. Allowlist-Based External Communication

Never let untrusted input control:
- Outbound URLs (use allowlists)
- Email recipients (verify against user records)
- Queue routing keys (use enums)

### 4. Orchestrator Pattern

If all three operations must happen in sequence, use a thin orchestrator that calls each isolated module:

```python
@app.route("/api/process-webhook", methods=["POST"])
def process_webhook():
    validated = input_handler.validate_webhook(request.json)
    user_data = data_layer.get_user_for_notification(validated.user_id)
    notifier.send_notification(user_data, validated.callback_url)
    return jsonify({"status": "ok"})
```

The orchestrator itself has no direct data access or external calls — it only coordinates.

## Connection to Real-World Exploits

| Attack Vector | Leg 1 | Leg 2 | Leg 3 |
|---|---|---|---|
| SSRF + credential theft | Internal API keys | Attacker URL in request | Outbound HTTP to attacker |
| SQLi + exfiltration | Database query results | Malicious SQL in input | Error sent to webhook |
| Prompt injection + tool use | RAG context / DB access | User prompt with injection | AI calls external API |
| XXE + data leak | Internal file read | Malicious XML payload | DNS/HTTP exfiltration |

## Guidance for Refactoring

When the trifecta audit flags a file:

1. **Identify each leg** — Mark which lines correspond to which leg
2. **Extract the most dangerous combination** — Usually leg 2 + leg 3 (input → external call)
3. **Create module boundaries** — Each leg gets its own file/class with a typed interface
4. **Add allowlists** — Any external destination must be pre-approved
5. **Test separation** — Verify that no single module can access all three capabilities
