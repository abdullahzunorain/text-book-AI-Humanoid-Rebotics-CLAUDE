<!-- 
  SYNC IMPACT REPORT
  ==================
  
  VERSION CHANGE: 0.0.0 (template) → 1.0.0 (initial ratification)
  RATIONALE: First official constitution for Physical AI Textbook MVP—major governance adoption
  
  PRINCIPLES ADDED: 6
  - I.   MVP-First (Minimal Scope)
  - II.  No Auth, No Personalization, No Translation
  - III. Content Scope (Introduction + Module 1 Only)
  - IV.  Chatbot Omnipresence
  - V.   Deployability & Demability
  - VI.  No Over-Engineering
  
  SECTIONS ADDED: 3
  - Development & Deployment Standards (technology stack, required delivery gates, testing, code standards)
  - Non-Goals (explicit scope exclusions)
  - Governance (amendment process, complexity justification, deployment gates)
  
  TEMPLATE CONSISTENCY CHECK:
  ✅ spec-template.md: Compliant—requirements must align with constitution's "no auth" and MVP scope
  ✅ plan-template.md: Compliant—"Constitution Check" gate will enforce tech stack and principle compliance
  ✅ tasks-template.md: Compliant—task categories will reflect MVP priorities (no personalization/auth tasks)
  ✅ phr-template.md: No changes needed
  ✅ checklist-template.md: No changes needed
  ✅ adr-template.md: No changes needed
  ✅ README.md: File does not exist yet; recommended to create with quickstart per "Code & Documentation Standards"
  
  FOLLOW-UP ACTIONS:
  1. Teams should review constitution and ensure all future specs start from P0/P1 user stories supporting MVP goal
  2. Code reviews must verify compliance with "Technology Stack" and "No Over-Engineering" principles
  3. When any architecturally significant decision is made, trigger ADR creation process per constitution gate
  4. Before first deployment, run "Required Before Deployment" checklist
  
  DATES: Ratified 2026-03-03, Last Amended 2026-03-03
-->

# Physical AI & Humanoid Robotics Textbook Constitution

## Purpose

Deploy a working Docusaurus-based interactive textbook with one module of content (ROS 2 Introduction) and an embedded RAG chatbot—all within the hackathon timeline. No auth, personalization, or translation features in this phase.

## Core Principles

### I. MVP-First (Minimal Scope)

Build only what is needed for a working, deployed, demonstrable MVP. Every feature must directly support the core deliverable: a published Docusaurus book + chatbot. Features are prioritized by deployment readiness and demo impact.

**Non-negotiable**: Remove features if they don't enable the MVP deadline. Anything deferred goes to post-MVP roadmap.

### II. No Auth, No Personalization, No Translation

This phase has explicit zero-scope for user authentication, account management, personalization, or multi-language support. The book is open, stateless, single-language, and publicly readable.

**Rationale**: These features multiply complexity and backend state; they will be added post-MVP if the product gains traction.

### III. Content Scope (Introduction + Module 1 Only)

The book ships with two content sections: (1) Introduction (landing/overview), (2) Module 1 (ROS 2 Fundamentals). Additional modules are planned post-MVP.

**Quality requirement**: Both sections MUST be complete, technically accurate, and formatted per Docusaurus standards before launch.

### IV. Chatbot Omnipresence

The RAG chatbot MUST be available on every page (sticky widget). Selected-text queries MUST work seamlessly—users can highlight text on any page and ask the chatbot questions about it.

**Success metric**: Chatbot loads in <2 seconds per page; selected-text query succeeds 95%+ of the time.

### V. Deployability & Demability

Every feature MUST be deployable and demoable within the hackathon timeline. No incomplete subsystems. Technical debt is acceptable if and only if it doesn't block deployment.

**Rule**: If a feature cannot be demoed live on deployed infrastructure, it does not ship in MVP.

### VI. No Over-Engineering

Keep the backend stateless and minimal. Keep the frontend simple. Use off-the-shelf tools where possible (Docusaurus for the book, existing RAG library for chatbot, cloud hosting for deployment). Custom code ONLY for MVP-critical differentiators.

**Constraint**: Reject any architectural proposal requiring >3 new services, custom frameworks, or novel data layer patterns.

## Development & Deployment Standards

### Technology Stack (Non-Negotiable)

- **Book Framework**: Docusaurus 3.x
- **Chatbot**: LLM-based RAG (e.g., LangChain, Semantic Kernel, or equivalent)
- **Backend**: Stateless API (FastAPI, Node.js, or similar); no custom ORM or DSL
- **Frontend**: Docusaurus default + minimal custom React components for chatbot widget
- **Hosting**: Static site (Vercel, Netlify, AWS S3+CloudFront) for book; serverless API for chatbot backend
- **Language**: Primary code in Python or TypeScript; content in Markdown

### Required Before Deployment

1. **Content Complete**: All sections in Intro + Module 1 written with code examples, diagrams, and clear learning outcomes
2. **Chatbot Tested**: Selected-text queries work on 5+ sample queries per page
3. **SEO & Analytics**: Basic Open Graph meta tags for book pages; simple analytics (Google Analytics or equivalent) to track user engagement
4. **Accessibility**: WCAG 2.1 Level AA compliance (alt text, keyboard navigation, heading hierarchy)
5. **Mobile-Responsive**: Book and chatbot widget render correctly on mobile, tablet, desktop

### Testing & Quality Assurance

- **Contract Tests**: API endpoints tested for correct schema and status codes
- **End-to-End**: Book pages load; chatbot widget renders; selected-text queries execute successfully
- **Performance**: Book pages load in <3 seconds on 4G network; chatbot queries respond in <5 seconds (p95)
- **Manual Testing**: Every page reviewed for typos, broken links, broken images, rendering issues

### Code & Documentation Standards

- **Minimal Commenting**: Code is self-documenting; comments only for "why", not "what"
- **README.md**: Must include quickstart instructions (clone, install, run, deploy) in <50 lines
- **API Documentation**: Auto-generated from code (Swagger/OpenAPI) or minimal markdown
- **Commit Messages**: Conventional format: `feat:`, `fix:`, `docs:`, `chore:` prefixes
- **No Hardcoded Secrets**: All config via `.env` files (local) or CI/CD secrets (deployed)

## Non-Goals

- User accounts, login, role-based access
- Multi-language support or i18n
- Personalized learning paths or quizzes
- Advanced search or full-text indexing beyond chatbot queries
- Content recommendation engine
- Mobile app (book is web-only)
- API rate limiting or usage metering

## Governance

**Constitution is law**: All design decisions, code reviews, and deployment approvals MUST verify compliance with these principles.

**Amendment Process**: 
1. Propose change with rationale and impact analysis
2. Discuss impact on schedule/scope
3. Approval required from technical lead + product lead
4. Document decision in ADR if architecturally significant
5. Update version number and last-amended date

**Complexity Justification**: If a task or proposal violates a principle, document why it's necessary and what tradeoff is accepted.

**Deployment Gate**: Every production deployment MUST verify:
- [ ] All principals principles honored (no hidden auth, features within scope, etc.)
- [ ] All required standards met (tests, mobile-responsive, <3s load time)
- [ ] Deployment is reversible (rollback plan in place)

**Version**: 1.0.0 | **Ratified**: 2026-03-03 | **Last Amended**: 2026-03-03
