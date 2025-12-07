# API Reference

Complete reference for all public APIs.

---

## DocumentProcessor

::: pyapu.processor.DocumentProcessor
options:
show_root_heading: true
members: - **init** - process

---

## Schema Types

::: pyapu.types.String
options:
show_root_heading: true

::: pyapu.types.Number
options:
show_root_heading: true

::: pyapu.types.Integer
options:
show_root_heading: true

::: pyapu.types.Boolean
options:
show_root_heading: true

::: pyapu.types.Array
options:
show_root_heading: true

::: pyapu.types.Object
options:
show_root_heading: true

---

## Plugin System

::: pyapu.plugins.registry.PluginRegistry
options:
show_root_heading: true
members: - register - get - list - discover

::: pyapu.plugins.registry.register
options:
show_root_heading: true

---

## Base Classes

::: pyapu.plugins.base.Provider
options:
show_root_heading: true

::: pyapu.plugins.base.Validator
options:
show_root_heading: true

::: pyapu.plugins.base.Postprocessor
options:
show_root_heading: true

::: pyapu.plugins.base.SecurityPlugin
options:
show_root_heading: true

---

## Security

::: pyapu.security.chain.SecurityChain
options:
show_root_heading: true

::: pyapu.security.sanitizer.InputSanitizer
options:
show_root_heading: true

::: pyapu.security.injection.PromptInjectionDetector
options:
show_root_heading: true

::: pyapu.security.output.OutputValidator
options:
show_root_heading: true

---

## Prompts

::: pyapu.prompts.builder.StructuredPrompt
options:
show_root_heading: true
members: - **init** - add_general_rule - add_field_rule - add_output_guideline - compile

---

## Pydantic Support

::: pyapu.pydantic_support.pydantic_to_schema
options:
show_root_heading: true

::: pyapu.pydantic_support.validate_with_pydantic
options:
show_root_heading: true

---

## Exceptions

::: pyapu.processor.SecurityError
options:
show_root_heading: true
