---
type: core-symbol-template
version: 1.0
description: Template structure for core symbol notes in unified Tolaria vault
wikilinks:
  - "[[CORE_SYMBOL_6966]]"
  - "[[[Elemental Force: Fire]]]"
---

## 📝 Core Symbol Note Structure

This template is automatically populated by the overnight research engine when creating new core symbol notes in Tolaria.

### Required Frontmatter Fields:

| Field | Description | Example Values |
|-------|-------------|----------------|
| type | Note category | `core-symbol` |
| symbol_id | Core gematria number | `124`, `666`, `963`, `55`, `111`, `279`, `777`, `13`, `888` |
| aliases | Alternative names/meanings | `universal bridge`, `completion`, `trinity` |
| name | Full symbol name | `Universal Bridge / Threshold` |
| domains | Domains where this appears | `political`, `military`, `religious`, `geographic` |
| elemental_force | Correlated elemental force | `fire`, `air`, `water`, `earth`, `lightning` |
| confidence_score | Pattern confidence (0.60-0.95) | `0.95`, `0.85` |
| occurrences | Number of occurrences found | `5`, `3`, `2` |
| created | First discovery timestamp | `"2026-04-29"` |
| last_modified | Last update timestamp | `"2026-04-29T01:45:06"` |
| tags | Categorization tags | `core`, `universal`, `bridge` |
| wikilinks | Related symbol notes (auto-populated) | `[[CORE_SYMBOL_666]]`, `[[ELEMENTAL_FORCE_FIRE]]` |

### Symbol Description Section:

Write the core meaning and reduction pathways for this symbol. Example:

```markdown
## {{SYMBOL_ID}} {{NAME}}

{{SHORT_DESCRIPTION}}

### Reduction Values:
- Primary: {{VALUE}} → {{REDUCED_VALUE}} (completion cycle)
- Secondary: {{ALTERNATIVE_PATH}}
```

### Domain Manifestations Table:

Create a table showing where this symbol appears across domains:

| Domain | Pattern Description | Value | Confidence |
|--------|-------------------|-------|------------|
| {{DOMAIN_1}} | {{PATTERN_EXPLANATION}} | {{VALUE}} | {{SCORE}} |
| {{DOMAIN_2}} | {{PATTERN_EXPLANATION}} | {{VALUE}} | {{SCORE}} |

### Relationship Matrix:

List related symbols and their connections:

- **[[CORE_SYMBOL_{{RELATED_SYM_1_ID}}]]** — {{RELATIONSHIP_TYPE}}
- **[[CORE_SYMBOL_{{RELATED_SYM_2_ID}}]]** — {{RELATIONSHIP_TYPE}}

---

## Example: [[CORE_SYMBOL_124]] Universal Bridge (Complete)

```yaml
type: core-symbol
symbol_id: 124
aliases: [universal bridge, threshold bridge, cubic measurement]
name: Universal Bridge / Threshold
domains:
  - general_gematria
  - political
  - military
elemental_force: null
confidence_score: 0.95
occurrences: 5
created: "2026-04-29"
last_modified: "2026-04-29T01:45:06"
tags: [core, universal, bridge]
wikilinks:
  - "[[CORE_SYMBOL_666]]"
  - "[[[Elemental Force: Fire]]]"
---

## [[124]] Universal Bridge / Threshold

The number **124** appears more than any other across all domains — not as date/code but as threshold. It serves as the universal bridge value connecting every domain.

### Manifestation Examples:

| Domain | Pattern Description | Value | Confidence |
|--------|-------------------|-------|------------|
| Volcano Programs | Volume measurement | 124 km³ | 0.95 |
| Sator Square | Symbolic convergence | 124 | 0.85 |
| Geographic Anchors | Trump Canada reference | 124 bridge | 0.90 |
| Stock Market | MAGMA/LUCY Japan plunge | 12.4% → 124 | 0.90 |

### Relationship Matrix:

- **[[CORE_SYMBOL_666]]** — Bridge provides threshold for completion cycles
- **[[CORE_SYMBOL_963]]** — Foundation before cycle turning begins
- **[[ELEMENTAL_FORCE_FIRE]]** — Volcanic manifestations of universal bridge

---

## Example: [[CORE_SYMBOL_666]] Completion (Complete)

```yaml
type: core-symbol
symbol_id: 666
aliases: [completion, wholeness, harmony]
name: Completion / Wholeness
domains:
  - general_gematria
elemental_force: fire
confidence_score: 0.95
occurrences: 1
created: "2026-04-29"
last_modified: "2026-04-29T01:39:51"
tags: [core, completion, wholeness]
wikilinks:
  - "[[CORE_SYMBOL_124]]"
---

## Completion / Wholeness [[666]]

The number **666** represents wholeness, harmony, integration — transforms to 9 via reduction. Appears across all elemental forces.

### Pigeon Imagery Examples:
- Tribunal resolution points
- Bottom marking completion cycles
- Spiral diagrams with "18, 36" → 9 completion

---

## Example: [[CORE_SYMBOL_777]] Trinity (Complete)

```yaml
type: core-symbol
symbol_id: 777
aliases: [trinity, completion, three-fold]
name: Trinity / Completion
domains:
  - religious
  - military
  - politics
elemental_force: fire
confidence_score: 0.95
occurrences: 1
created: "2026-04-29"
tags: [core, trinity, universal]
wikilinks:
  - "[[CORE_SYMBOL_666]]"
---

## Trinity / Completion [[777]]

Complete trinity cycle appearing in religious, military, and political domains with fire elemental force.
```

---

## ✏️ When Creating New Notes:

1. **Start with YAML frontmatter** — Use template structure above
2. **Add wikilinks automatically** — Connect to related symbols/forces
3. **Populate domain table** — Show where symbol appears across domains
4. **Add relationship section** — Link to 2-4 most relevant related notes
5. **Set confidence score** — Based on occurrence frequency and pattern strength
