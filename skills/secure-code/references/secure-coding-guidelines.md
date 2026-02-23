# Secure Coding Guidelines

Reference guide for remediating common vulnerability classes. Load this when fixing specific finding types.

---

## Injection (CWE-89, CWE-78, CWE-94)

### SQL Injection

**Why dangerous:** Attacker-controlled input in SQL queries can read, modify, or delete arbitrary data.

**Correct pattern:**
```python
# Parameterized queries — values never interpolated into SQL
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```javascript
// Prepared statements
const result = await db.query("SELECT * FROM users WHERE id = $1", [userId]);
```

**Incorrect pattern:**
```python
# String interpolation — NEVER do this
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Command Injection (CWE-78)

**Why dangerous:** User input in shell commands enables arbitrary command execution.

**Correct pattern:**
```python
# Use list form, never shell=True with user input
subprocess.run(["convert", filename, "output.png"], check=True)
```

**Incorrect pattern:**
```python
subprocess.run(f"convert {filename} output.png", shell=True)
```

### Code Injection (CWE-94)

**Correct pattern:** Avoid `eval()`, `exec()`, `Function()` with user input entirely. Use structured parsers instead.

---

## Authentication & Session (CWE-287, CWE-384)

### Broken Authentication

**Correct patterns:**
- Use established auth libraries (passport, next-auth, django.contrib.auth)
- Hash passwords with bcrypt/argon2 (cost factor >= 10)
- Implement rate limiting on login endpoints
- Use constant-time comparison for tokens

**Incorrect patterns:**
- Rolling custom auth/session logic
- Storing passwords in plaintext or with MD5/SHA1
- Comparing tokens with `==` (timing attack)

---

## Cryptography (CWE-327, CWE-330)

### Weak Cryptography

**Correct patterns:**
- AES-256-GCM for symmetric encryption
- RSA-2048+ or Ed25519 for asymmetric
- `secrets` module (Python) or `crypto.randomBytes` (Node) for random values
- Never hardcode keys or IVs

**Incorrect patterns:**
- DES, RC4, ECB mode
- `random.random()` or `Math.random()` for security-sensitive values
- Hardcoded encryption keys

---

## Data Exposure (CWE-200, CWE-532)

### Sensitive Data in Logs

**Correct pattern:**
```python
logger.info("User login", extra={"user_id": user.id})  # No PII
```

**Incorrect pattern:**
```python
logger.info(f"Login: email={email}, password={password}")
```

### Secrets in Source

- Use environment variables or secret managers
- Never commit `.env` files, API keys, or credentials
- Add secrets patterns to `.gitignore`

---

## Server-Side Request Forgery (CWE-918)

**Why dangerous:** Attacker-controlled URLs in server-side HTTP requests can access internal services.

**Correct patterns:**
- Allowlist permitted hostnames/IPs
- Block private/internal IP ranges (10.x, 172.16-31.x, 192.168.x, 169.254.x, 127.x)
- Validate URL scheme (https only)
- Use DNS resolution checks before connecting

**Incorrect pattern:**
```python
# User controls the URL entirely
response = requests.get(user_provided_url)
```

---

## Cross-Site Scripting (CWE-79)

**Correct patterns:**
- Use framework auto-escaping (React JSX, Django templates, Jinja2 autoescape)
- Sanitize HTML with allowlists (DOMPurify, bleach)
- Set `Content-Security-Policy` headers

**Incorrect patterns:**
- `dangerouslySetInnerHTML` with unsanitized input
- Template literal injection in HTML
- `innerHTML = userInput`

---

## Path Traversal (CWE-22)

**Correct patterns:**
```python
# Resolve and verify the path stays within allowed directory
safe_path = Path(base_dir).joinpath(user_filename).resolve()
if not safe_path.is_relative_to(Path(base_dir).resolve()):
    raise ValueError("Path traversal attempt")
```

**Incorrect pattern:**
```python
open(os.path.join(upload_dir, user_filename))  # ../../../etc/passwd
```

---

## Deserialization (CWE-502)

**Correct patterns:**
- Use JSON for data interchange
- If YAML needed, use `yaml.safe_load()` only
- Never use `pickle.loads()` on untrusted data

**Incorrect patterns:**
```python
data = pickle.loads(request.body)      # Arbitrary code execution
data = yaml.load(request.body)         # Unsafe by default in older PyYAML
```

---

## Mass Assignment (CWE-915)

**Correct pattern:**
```python
# Explicit field allowlist
user.update(name=data["name"], email=data["email"])
```

**Incorrect pattern:**
```python
user.update(**request.json)  # Attacker sets is_admin=true
```

---

## Language-Specific Notes

### Python
- Use `secrets` not `random` for tokens
- Use `shlex.quote()` if shell commands are unavoidable
- Use `defusedxml` for XML parsing (XXE prevention)

### JavaScript/TypeScript
- Use `helmet` middleware for HTTP security headers
- Use `express-rate-limit` for brute force protection
- Avoid `eval()`, `new Function()`, `vm.runInNewContext()` with user input

### Go
- Use `html/template` not `text/template` for HTML
- Use `crypto/rand` not `math/rand` for security
- Use prepared statements with `database/sql`

---

For deep dives, see: [OWASP Top 10](https://owasp.org/www-project-top-ten/), [CWE Top 25](https://cwe.mitre.org/top25/)
