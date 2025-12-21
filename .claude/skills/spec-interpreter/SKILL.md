---
name: spec-interpreter
description: Read and interpret specification files from specs/phase2/ to understand feature requirements, user stories, acceptance criteria, and API contracts. Use when (1) implementing any feature, (2) user asks "what does the spec say about X?", (3) another skill needs spec information, or (4) clarification is needed about requirements before beginning work.
license: Complete terms in LICENSE.txt
---

# Spec Interpreter

Locate, read, and extract information from specification files to inform feature implementation and answer questions about requirements.

## Workflow

Follow these steps when interpreting specs:

1. **Locate relevant spec files** in `specs/phase2/`
   - Features: `specs/phase2/features/[name].md`
   - API contracts: `specs/phase2/api/[name].md`
   - Database schemas: `specs/phase2/database/schema.md`

2. **Extract key information**
   - User stories (preserve "As a [role], I want [goal], so that [benefit]" format)
   - Acceptance criteria (preserve "Given... When... Then..." format verbatim)
   - API contracts (endpoints, request/response schemas, validation rules)
   - Database requirements (tables, fields, relationships, constraints)

3. **Identify relationships between specs**
   - Which API endpoints support which features
   - Which database tables are needed for which features
   - Dependencies between features

4. **Detect gaps or ambiguities**
   - Missing acceptance criteria
   - Undefined API contracts
   - Ambiguous requirements that need clarification
   - Inconsistencies between related specs

## Output Format

Present spec analysis using this structure:

```
📋 Spec Analysis: [feature-name]

Source: specs/phase2/features/[name].md

User Stories:
- As a [role], I want [goal], so that [benefit]
- [Additional stories...]

Acceptance Criteria:
1. Given [context]
   When [action]
   Then [expected outcome]

2. [Additional criteria...]

Related Specs:
- API: specs/phase2/api/[endpoint].md
- Database: specs/phase2/database/schema.md
- Dependencies: [other feature specs]

Gaps/Questions:
- [Any missing or ambiguous requirements]
- [Suggested clarifications needed]
```

## Key Rules

- **Always cite spec file paths** - Include full paths to source files
- **Extract verbatim** - Copy acceptance criteria and user stories exactly as written; do not paraphrase
- **Identify missing specs** - If a required spec doesn't exist, suggest creating it before implementation
- **Surface ambiguities** - Call out unclear or contradictory requirements for user clarification
- **Maintain traceability** - Link features to their API and database dependencies
- **Don't assume** - If spec is silent on a requirement, ask rather than filling gaps with assumptions
