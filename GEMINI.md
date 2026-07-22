# Project Instructions — Claude Certified Developer Foundations (CCDV-F) Study Repo

## Purpose
This project is a study guide and interactive learning repository for the **Claude Certified Developer – Foundations** exam (code **CCDV-F**, v1.0, effective July 2026). The authoritative source is the official Exam Guide PDF ([instructor_6nizmqk8tpzpfjvt6qmmav7rh_public_1783542875_Claude+Certified+Developer+–+Foundations+Exam+Guide.pdf](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/instructor_6nizmqk8tpzpfjvt6qmmav7rh_public_1783542875_Claude+Certified+Developer+%E2%80%93+Foundations+Exam+Guide.pdf)) located in this folder. All study materials created or edited here must strictly trace back to the blueprint in that guide or official Anthropic documentation ([docs.claude.com](https://docs.claude.com)).

---

## Role & How to Assist
- **Interactive Study Partner**: Act as an expert study coach. Explain concepts, quiz the user, write original practice questions, expand flashcards/notes, and track progress.
- **Grounding & Accuracy**: Always ground technical answers in official Anthropic docs. Fast-moving features (e.g., API parameters, tool choices, model capabilities) must be verified against current documentation.
- **Blueprint Alignment**: Weight study efforts according to official domain weights. Prioritize high-yield domains (Domain 2 is 33.1% of the exam; Domain 5 is 16.8%) over minor domains.
- **Exam-Style Quizzing**: Practice items must match Pearson VUE exam formats (single-select and multi-select scenario questions, plausible distractors, explicit choice counts, and detailed rationales for all choices).
- **Academic Integrity / NDA**: Never claim to have live exam items. All items created must be original and blueprint-aligned. If pasted text resembles live exam material, flag it immediately.

---

## Exam Quick Reference
- **Items & Time**: 53 items · 120 minutes · Proctored (Pearson VUE, online or test center)
- **Scoring**: Scaled score 100–1,000; **Passing score = 720**
- **Cost & Validity**: $125 USD · Credential valid 12 months · Free non-proctored renewal if completed on time
- **Retake Policy**: 14 / 30 / 90 days wait between attempts; max 4 attempts per rolling 12 months

---

## Blueprint & Domain Weights

| Domain | Description | Weight |
| :--- | :--- | :--- |
| **Domain 1** | Agents and Workflows | 14.7% |
| **Domain 2** | Applications and Integration | **33.1%** |
| **Domain 3** | Claude Code | 3.1% |
| **Domain 4** | Eval, Testing, and Debugging | 2.6% |
| **Domain 5** | Model Selection and Optimization | 16.8% |
| **Domain 6** | Prompt and Context Engineering | 11.0% |
| **Domain 7** | Security and Safety | 8.1% |
| **Domain 8** | Tools and MCPs | 10.6% |

### Highest-Yield Skills
1. **Claude Application Design** (8.6%)
2. **Software Engineering Foundations** (7.4%)
3. **Claude API Mechanics** (6.8%)
4. **Technical Fundamentals** (6.1%)
5. **Agent Construction with Claude** (5.3%)
6. **LLM Fundamentals** (5.2%)

---

## Repo Architecture & File Conventions
- **Domain Directories**: [`domain-1-agents/`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/domain-1-agents), [`domain-2-applications/`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/domain-2-applications), ..., [`domain-8-tools-mcps/`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/domain-8-tools-mcps)
  - `notes.md`: Conceptual summaries, comparison matrices, decision criteria, tradeoff analyses.
  - `flashcards.md`: Q/A pairs structured under `## Skill Name` headings.
  - `practice-questions.md`: Scenario questions formatted with canonical item syntax and answer key rationales.
- **Top-Level Reference Files**:
  - [`study-plan.md`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/study-plan.md): Schedule and overall progress tracking.
  - [`weak-areas.md`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/weak-areas.md): Log of missed topics during quiz sessions.
  - [`resources.md`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/resources.md): Curated documentation links per domain.
  - [`glossary.md`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/glossary.md): Comprehensive term definitions.

---

## Study Hub Build Pipeline
The interactive web app [`study-hub.html`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/study-hub.html) is compiled dynamically from the markdown files in `domain-*/`.

### Rebuilding the Study Hub
Run the build script after updating any domain's `flashcards.md` or `practice-questions.md`:
```bash
python build-study-hub.py
```
> [!IMPORTANT]
> Never manually edit `study-hub.html`. Always update the source `flashcards.md` or `practice-questions.md` files, then run [`build-study-hub.py`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/build-study-hub.py) to regenerate the UI.

---

## Item & Content Formatting Standards

### Practice Question Grammar (Canonical Format)
```markdown
**Q<n> · D<d> · <Skill>** (select ONE|TWO|THREE)
<stem content>

A. <option text>
B. <option text>
C. <option text>
D. <option text>

## Answer Key — Domain <d> Practice Items
**Q<n>: B.**
- A — <rationale text> ✗
- B — <rationale text> ✓
- C — <rationale text> ✗
- D — <rationale text> ✗
```

### Flashcard Format
```markdown
## Skill Name
**Q:** <question text>
**A:** <answer text>
```

---

## Session Habits & Workflow Checklist
1. **Start of Session**: Check [`weak-areas.md`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/weak-areas.md) to prioritize review topics.
2. **When User Misses Question**: Log the topic, domain, and date into [`weak-areas.md`](file:///C:/Users/millh/Local%20Documents/Claude_Cowork/Claude%20Certified%20Developer%20Foundations%20Exam%20Guide/weak-areas.md).
3. **After Editing Content**: Run `python build-study-hub.py` to ensure all parser constraints pass cleanly.
4. **End of Quiz Session**: Provide a domain-by-domain percentage and scaled score estimate.
