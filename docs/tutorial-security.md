# Input Sanitization

Clean and validate inputs to reduce prompt injection risks.

> [!WARNING] > **Honest disclaimer:** These are sanitization tools, not a complete security solution.
> Syntactic cleaning (whitespace, HTML removal) does NOT prevent semantic prompt injection.
> A sophisticated attacker can craft prompts that bypass pattern-based detection.
> Use these as **defense-in-depth**, not as your only protection.

---

## What It Does (and Doesn't)

| Feature             | Protects Against                                       | Does NOT Protect Against      |
| ------------------- | ------------------------------------------------------ | ----------------------------- |
| `PromptSanitizer`   | Malformed input, control chars, excessively long input | Semantic jailbreaks           |
| `InjectionDetector` | Common injection phrases                               | Novel/obfuscated injections   |
| `PIIRedactor`       | Accidental PII exposure                                | Intentional data exfiltration |

---

## Sanitization Chain

```python
from strutex import DocumentProcessor, GeminiProvider
from strutex.security import SanitizationChain, InjectionDetector, PromptSanitizer

# Create sanitization chain
sanitizers = SanitizationChain([
    PromptSanitizer(remove_html=True, max_length=10000),
    InjectionDetector()
])

processor = DocumentProcessor(
    provider=GeminiProvider(),
    security=sanitizers  # Still uses 'security' param for backwards compat
)

result = processor.process("invoice.pdf", prompt, schema=MySchema)
```

---

## PromptSanitizer

Cleans input before sending to LLM:

```python
from strutex.security import PromptSanitizer

sanitizer = PromptSanitizer(
    remove_html=True,           # Strip HTML tags
    remove_control_chars=True,  # Strip \x00, etc.
    collapse_whitespace=True,   # Normalize spaces
    max_length=10000            # Truncate long input
)
```

---

## InjectionDetector

Pattern-based detection of common injection attempts:

```python
from strutex.security import InjectionDetector

detector = InjectionDetector(
    patterns=[
        r"ignore previous instructions",
        r"disregard all",
        r"you are now",
        r"forget everything",
    ]
)

# Raises SanitizationError if pattern matches
```

> [!CAUTION]  
> Pattern matching is **easily bypassed**. Attackers can use typos, Unicode  
> lookalikes, or rephrasing to evade detection. Don't rely on this alone.

---

## PIIRedactor

Redact sensitive data from outputs:

```python
from strutex.security import PIIRedactor

redactor = PIIRedactor(
    patterns={
        "ssn": r"\d{3}-\d{2}-\d{4}",
        "credit_card": r"\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    },
    replacement="[REDACTED]"
)

# {"ssn": "123-45-6789"} → {"ssn": "[REDACTED]"}
```

---

## Best Practices

| Scenario                  | Recommendation                       |
| ------------------------- | ------------------------------------ |
| **User-provided prompts** | `PromptSanitizer` + length limits    |
| **Untrusted documents**   | Don't extract prompts from documents |
| **Sensitive output**      | `PIIRedactor` as defense-in-depth    |
| **High security needs**   | Human review of outputs              |

---

## What You Should Actually Do

1. **Don't trust LLM output** — Validate with Pydantic schemas
2. **Limit prompt sources** — Don't let users write arbitrary prompts
3. **Log everything** — Audit trail for incident response
4. **Set output length limits** — Prevent exfiltration via verbose output
5. **Use structured extraction** — Schema constraints limit attack surface

---

## Error Handling

```python
from strutex.security import SanitizationError

try:
    result = processor.process("doc.pdf", user_prompt, schema=MySchema)
except SanitizationError as e:
    print(f"Input rejected: {e}")
    # Log attempt, don't process
```

---

## Next Steps

| Want to...         | Go to...                                     |
| ------------------ | -------------------------------------------- |
| Process in batches | [Batch Processing](tutorial-batch.md)        |
| Handle errors      | [Error Handling](tutorial-error-handling.md) |
