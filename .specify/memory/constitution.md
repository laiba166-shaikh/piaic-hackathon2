<!--
Sync Impact Report:
Version Change: Initial → 1.1.0
Modified Principles:
  - PRINCIPLE_1_NAME → I. Spec-Driven Development
  - PRINCIPLE_2_NAME → II. Clean Code and Proper Structure
  - PRINCIPLE_3_NAME → III. Test-First (NON-NEGOTIABLE)
  - PRINCIPLE_4_NAME → IV. Version Control and CI/CD
  - PRINCIPLE_5_NAME → V. Observability and Logging
Added Sections:
  - Additional Constraints (Performance Standards, Security Requirements, Success Criteria, Compliance and Regulatory Standards)
  - Development Workflow (Spec-Driven Implementation, Code Review and Quality Gates)
  - Technology Stack
Removed Sections: None
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligned
  ✅ .specify/templates/spec-template.md - Requirements section aligned
  ✅ .specify/templates/tasks-template.md - Test-first task organization aligned
Follow-up TODOs: None
-->

# Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven Development

Spec-driven development is at the core of this project. Every feature, no matter how small, MUST have a markdown specification in the `/specs` folder. Claude Code will generate the code based on these specifications, and the code MUST meet the defined requirements before it is considered complete. Features are not to be manually coded but MUST evolve through iterative refinement of the specification until the generated code is correct.

**Mandatory Spec Reference Rule (NON-NEGOTIABLE):**

1. **NO implementation without reading the spec first** - Before writing ANY code (including tests), the relevant specification file(s) MUST be read and understood
2. **Explicit spec references required** - All implementation work MUST reference the spec file by path (e.g., `@specs/002-phase2-fullstack-web/features/01-user-authentication.md`)
3. **Architecture documents are specifications** - Backend architecture (`00-backend-architecture.md`), frontend design flow (`08-frontend-design-flow.md`), API contracts, and database schemas are authoritative specifications that MUST be consulted
4. **CLAUDE.md files guide implementation** - Frontend and backend CLAUDE.md files provide context-specific guidelines and MUST be referenced when working in those directories
5. **Verification checkpoint** - Before submitting code, verify that the implementation matches ALL requirements in the referenced spec(s)

**Enforcement:**
- Pull requests MUST cite which spec file(s) were implemented
- Code reviews MUST verify spec compliance
- Automated tests MUST validate spec acceptance criteria
- Non-compliance requires rework and spec re-review

**Rationale:** Ensures requirements are documented, testable, and drive implementation rather than being retrofitted after coding. This approach enables AI-assisted development and maintains architectural clarity. Mandatory spec references prevent developers from "guessing" requirements, reduce rework, and ensure every line of code traces to documented intent.

### II. Clean Code and Proper Structure

The project MUST follow clean code principles:

- **Readable Code:** Code MUST be easy to read and understand by anyone familiar with the project
- **Modularity:** Use functions, classes, and modules that have a single responsibility and are easy to test
- **Scalability:** Ensure that the project is easily extendable for future features
- **Use of Type Hints:** Python type hints MUST be used for better code clarity and to leverage static analysis tools

**Rationale:** Maintainable code reduces technical debt, facilitates team collaboration, and enables confident refactoring. Type hints provide self-documenting code and catch errors early.

### III. Test-First (NON-NEGOTIABLE)

Test-Driven Development (TDD) will be followed rigorously:

1. **Write Tests First:** All tests for a new feature MUST be written before the implementation begins
2. **Red-Green-Refactor Cycle:** The cycle MUST be strictly followed — write a test, observe it fail, implement functionality, and then refactor the code
3. **Test Automation:** Unit tests, integration tests, and end-to-end tests MUST be automated. All tests MUST be run during the CI process

**Rationale:** TDD ensures requirements are testable, reduces defects, provides executable documentation, and enables confident refactoring. The red phase proves tests can fail; the green phase proves the implementation works; refactoring improves design without breaking functionality.

### IV. Version Control and CI/CD

- **GitHub Repository:** The source code will be hosted in a public GitHub repository. Each phase MUST be submitted through pull requests
- **CI/CD Integration:** GitHub Actions or equivalent CI tools MUST be used to ensure automated testing and build processes are in place
- **Versioning:** Use semantic versioning (MAJOR.MINOR.PATCH) for version control

**Rationale:** Version control provides audit trails, enables collaboration, and facilitates rollback. CI/CD automates quality gates and accelerates deployment cycles while maintaining reliability.

### V. Observability and Logging

Structured logging and observability tools MUST be integrated throughout the project. This will help in troubleshooting, identifying bottlenecks, and improving the application's performance. Logs MUST be detailed and consistent, including:

- Error logging with stack traces
- Event-based logging for key operations (e.g., adding a task, marking a task complete)
- Performance monitoring logs (e.g., time to complete CRUD operations)

**Rationale:** Production systems fail; observability enables rapid diagnosis, performance optimization, and evidence-based architectural decisions. Structured logs enable aggregation, search, and automated alerting.

## Additional Constraints

### I. Performance Standards

- **Time Complexity:** Ensure that all CRUD operations (Create, Read, Update, Delete) on tasks are optimized for performance, particularly as the system scales
  - **Read Operations:** These MUST be optimized for speed (e.g., using indexing)
  - **Write Operations:** MUST have minimal latency (e.g., using efficient data structures)
- **Database Query Optimization:** Use proper indexing and query optimization techniques for better performance, especially as the database grows
- **Efficient Task Operations:** Actions such as creating, updating, or deleting tasks MUST be completed in less than 500 milliseconds under normal load

**Rationale:** User experience degrades sharply beyond 200ms response times. Optimization constraints prevent performance regressions and ensure the system remains responsive at scale.

### II. Security Requirements

Security is a top priority, especially as the project progresses through different phases:

- **Authentication and Authorization:** Implement secure user authentication (using JWT or other token-based systems) for the web and AI chatbot phases. Ensure that each user can only access their own data
- **Data Protection:** All sensitive information (e.g., passwords, user data) MUST be encrypted both in transit and at rest
- **Secure Dependencies:** Only use well-vetted libraries and frameworks. Regularly check for security vulnerabilities in the dependencies via tools like `dependabot`
- **SQL Injection Protection:** Ensure that the application uses parameterized queries to prevent SQL injection attacks
- **Cross-Site Scripting (XSS) Protection:** Ensure all user input is sanitized, particularly in the web application and chatbot interfaces

**Rationale:** Security breaches have legal, financial, and reputational consequences. Defense-in-depth (authentication, encryption, input validation) mitigates risk at multiple layers.

### III. Success Criteria

The project will be considered successful if it meets the following criteria:

1. **Functionality Completion:**
   - All core features (Add, Delete, Update, View, Mark Complete) are implemented in the CLI application and work flawlessly
   - Each feature of the web application is implemented and behaves as specified
   - The AI-powered chatbot is able to manage tasks via natural language and integrates well with the backend services

2. **Code Quality:**
   - Code MUST adhere to clean code practices and maintainable software architecture
   - The project passes all automated tests and the code meets the required quality gates

3. **Performance:**
   - CRUD operations MUST perform efficiently, with minimal response time under typical use conditions

4. **Security:**
   - All data MUST be securely handled, and no security vulnerabilities should exist in the system

5. **User Experience (UX):**
   - The user interface (CLI, web, and chatbot) MUST be intuitive and easy to use
   - All actions MUST be quick, with minimal latency

6. **Documentation:**
   - Documentation MUST be complete and accurate, with instructions on setup, use, and contribution to the project
   - The specification files MUST be clear, well-organized, and up to date

**Rationale:** Measurable success criteria prevent scope creep, align stakeholder expectations, and provide objective acceptance gates for deliverables.

### IV. Compliance and Regulatory Standards

- **GDPR Compliance:** Ensure that user data is handled in compliance with GDPR or relevant data protection laws (e.g., anonymizing data where applicable)
- **Licensing:** Ensure that the project and any third-party dependencies used are licensed appropriately. The code repository MUST include a proper open-source license (e.g., MIT)

**Rationale:** Legal compliance is non-negotiable. Open-source licensing enables community contribution while protecting contributors from liability.

## Development Workflow

### Spec-Driven Implementation

**MANDATORY WORKFLOW - MUST be followed for ALL implementation work:**

**Step 1: Identify and Read Specifications**
1. Locate the relevant spec file(s) in `/specs/[phase]/features/[feature-name].md`
2. Read the complete specification including:
   - Feature overview and user stories
   - Acceptance criteria (ALL must be met)
   - API contracts (if applicable)
   - Data models and database schema
   - UI/UX requirements
   - Error handling and edge cases
3. Read applicable architecture documents:
   - Backend: `@specs/002-phase2-fullstack-web/00-backend-architecture.md`
   - Frontend: `@specs/002-phase2-fullstack-web/08-frontend-design-flow.md`
   - API: `@specs/002-phase2-fullstack-web/api/rest-endpoints.md`
   - Database: `@specs/002-phase2-fullstack-web/database/schema.md`
4. Read context-specific guidelines:
   - Frontend work: `@frontend/CLAUDE.md`
   - Backend work: `@backend/CLAUDE.md`

**Step 2: Plan Implementation**
1. Review the plan.md file for the feature (if it exists)
2. Review the tasks.md file for specific implementation tasks
3. Identify which acceptance criteria you will implement
4. Note any dependencies on other specs or features

**Step 3: Write Tests First (TDD)**
1. Write failing tests based on spec acceptance criteria
2. Reference the spec file in test comments
3. Ensure tests cover ALL acceptance criteria

**Step 4: Implement Code**
1. Use Claude Code to generate implementation based on spec
2. Reference spec file(s) in code comments where appropriate
3. Follow patterns from architecture documents and CLAUDE.md files
4. Verify implementation matches spec requirements

**Step 5: Verify Spec Compliance**
1. Run all tests and ensure they pass
2. Review acceptance criteria - ALL must be satisfied
3. Check error handling and edge cases from spec
4. Verify performance requirements are met

**Step 6: Document Spec References**
1. In commit messages, cite spec file(s): `Implement user auth from @specs/.../01-user-authentication.md`
2. In pull requests, list all spec files implemented
3. In code reviews, verify spec compliance

**CHECKPOINT:** If ANY step reveals ambiguity or missing information in the spec, STOP implementation and update the spec first. Never guess or assume requirements.

**Rationale:** Specifications as single source of truth prevent ambiguity, enable parallel work, and facilitate AI-assisted development. Iteration based on tests ensures convergence to correct implementation. The mandatory workflow ensures specifications drive development, not the reverse.

### Code Review and Quality Gates

**Every pull request MUST pass these gates:**

1. **Spec Compliance Review (MANDATORY):**
   - PR description MUST list all spec file(s) implemented (with full paths)
   - Code reviewer MUST verify each acceptance criterion from spec is met
   - Code reviewer MUST verify architecture patterns from referenced docs are followed
   - Code reviewer MUST verify CLAUDE.md guidelines are followed (if applicable)
   - **GATE:** PR cannot be approved without spec file references and compliance verification

2. **Code Quality Review:**
   - Code MUST be clean, readable, and maintainable
   - Code MUST follow patterns from architecture documents
   - Code MUST not introduce security vulnerabilities
   - Code MUST include appropriate error handling
   - **GATE:** Code quality issues must be resolved before merge

3. **Automated Testing:**
   - All tests MUST pass on CI/CD pipeline
   - No new failing tests are introduced
   - Tests MUST validate spec acceptance criteria
   - **GATE:** Failing tests block merge

4. **Test Coverage:**
   - Achieve at least 90% test coverage for new code
   - Maintain low rate of code duplication
   - **GATE:** Coverage below 90% requires justification or additional tests

**Pull Request Template:**
```markdown
## Implemented Specifications
- [ ] @specs/[phase]/features/[feature].md - [Feature Name]
- [ ] @specs/[phase]/[architecture-doc].md (if applicable)
- [ ] @frontend/CLAUDE.md or @backend/CLAUDE.md (if applicable)

## Acceptance Criteria Checklist
- [ ] Criterion 1 from spec (describe)
- [ ] Criterion 2 from spec (describe)
- [ ] All edge cases handled per spec
- [ ] Error handling implemented per spec

## Architecture Compliance
- [ ] Follows patterns from architecture documents
- [ ] Follows CLAUDE.md guidelines
- [ ] Security requirements met
- [ ] Performance requirements met

## Testing
- [ ] All tests pass
- [ ] Test coverage ≥ 90%
- [ ] Tests validate spec acceptance criteria
```

**Rationale:** Peer review catches design issues automation cannot detect. High code coverage ensures comprehensive testing. Combined gates maintain quality bar and facilitate knowledge sharing. Mandatory spec compliance verification ensures every PR traces to documented requirements, preventing scope drift and undocumented features.

## Technology Stack

- **Backend/CLI:** Python 3.13+, UV
- **Spec-Driven Development Tools:** Claude Code, Spec-Kit Plus
- **Web Application:** Next.js, FastAPI, SQLModel, Neon Serverless PostgreSQL
- **Authentication:** Better Auth, JWT
- **Chatbot Framework:** OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK
- **Performance Tools:** Query Optimization, SQL Indexing
- **Security:** Encryption, JWT Authentication, Secure Dependencies
- **CI/CD:** GitHub Actions

**Rationale:** Technology choices align with project phases (CLI → Web → AI → Cloud), leverage modern AI capabilities, and use proven tools that support rapid iteration and scalability.

## Governance

- **Amendments:** Changes to the constitution MUST be documented, with approval from the project leadership and a migration plan
- **Code Ownership:** Each feature will have a designated owner responsible for the implementation and maintenance of that feature across all phases
- **Compliance:** All features MUST comply with the security, performance, and success criteria outlined in this document
- **Audit and Review:** Regular code audits and reviews will be conducted to ensure that the project adheres to the constitution and the required standards

**Rationale:** Governance ensures constitutional stability while allowing evolution. Code ownership creates accountability. Regular audits verify compliance and catch drift before it compounds.

**Version**: 1.2.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-26
