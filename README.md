# PoliticalNLP 2026 research companion

Prompts, contextual cards and research code accompanying **From News Streams to Narrative Intelligence Briefs: LLM-Assisted Political Discourse Analysis in the Hungarian 2026 Pre-Election Context**, by Ekaterina Loginova, Maksim Ermakov and Stephan Khramov.

[Read the paper](https://lrec.elra.info/lrec2026-ws-politicalnlp-01) · [DOI: 10.63317/228tnds8d6kd](https://doi.org/10.63317/228tnds8d6kd) · [Citation](CITATION.bib) · [Aletheos](https://aletheos.team/)

## Who this is for and how to use it

For researchers inspecting the published method, developers assessing a prompt/processing building block for another study, and educators discussing evidence and failure analysis. Start with the question, inspect the relevant prompt/card/code and its limits, then record the exact commit and missing inputs before adaptation.

Use cases include examining how a narrative-frame or brief template represents evidence, comparing the research design with manual/alternative analysis, and identifying which corpus/run/annotation material a reproduction would require. This is a research artifact, not a hosted monitoring product or advertised subscription. The study, shared materials and a new reproduction/validated deployment remain separate.

## The research question

How can a large political-news stream become a structured brief that an analyst can inspect and challenge? The published Hungarian election case study connects narrative-frame extraction, manipulation analysis, clustering and brief generation. Its evaluation and failure analysis concern that study; they do not establish general accuracy for Aletheos tools.

This public companion supports inspection of the method and its building blocks. It does not include the study's article corpus, recorded runs or evaluation annotations, and it is not a frozen end-to-end reproduction package.

## Explore the materials

| Material | What to inspect |
| --- | --- |
| [Narrative-frame prompt](prompts/prompt-narrative-frame-extractor.txt) | Actors, portrayed roles, actions, targets and causal claims, with instructions to avoid unsupported inference. |
| [Manipulation prompt](prompts/prompt-manipulation-extractor.txt) | The technique-extraction instructions and output structure. |
| [Brief system instructions](prompts/system_prompt.txt) and [brief input/output template](prompts/user_prompt_template.txt) | The five-section narrative-intelligence brief design, evidence constraints and contextual-card inputs. |
| [Article-summary export](prompts/prompt-npf-summary.txt) | A separate NPF article-summary prompt. This saved export is truncated and is not the brief-generation template. |
| [Evaluation prompt](prompts/prompt-npf-judge.txt) | The criteria supplied to the model judge; this is an evaluation instrument, not a set of human labels or measured results. |
| [Contextual cards](contextual_cards/) | Domain-specific context supplied for the research design. Inspect each card's content and references in context. |
| [Processing modules](src/political_nlp/) | Article collection, extraction, clustering and report-building code. See the implementation limits below before adapting it. |

The JSON files beside the exported prompt text retain configuration information, but valid outer JSON does not establish a complete executable template. The article-summary export preserves truncated text and its configuration is a string. The local prompt constants and exported templates are separate artefacts; this repository does not establish that they are interchangeable or identify a complete archived run.

## Inspect without provider accounts

Clone the public repository:

```bash
git clone https://github.com/aletheos-ngo/politicalNLP2026.git
cd politicalNLP2026
```

The prompts, cards and code can be read without installing dependencies or adding API keys. To inspect one exported prompt as JSON using Python's standard library:

```bash
python -m json.tool prompts/prompt-narrative-frame-extractor.json
```

For a citation or comparison, record the exact commit you inspected:

```bash
git rev-parse HEAD
```

## Reproducibility and adaptation

[Reproducibility notes](docs/reproducibility.md) distinguish the published study, the shared artefacts and the current implementation. They identify concrete integration issues in the entrypoint, parsing and report generation, as well as the missing frozen environment and study records.

The code is available for inspection, but a full pipeline run has not been validated as part of this handoff. The old full-pipeline quick-start is therefore replaced by the inspection path above. Running or adapting the processing modules requires reviewing dependencies, provider/model configuration, input permissions and costs first. The source uses `datetime.UTC`, which requires Python 3.11 or newer; this is a source requirement, not a tested dependency environment.

Some processing stages call external AI services or download models. Reading the companion materials does neither. Keep credentials outside version control and use only material permitted for the chosen processing and provider arrangement.

## Cite the study

Use the publication's author names and bibliographic record. A ready-to-copy entry is in [CITATION.bib](CITATION.bib):

> Ekaterina Loginova, Maksim Ermakov and Stephan Khramov. 2026. *From News Streams to Narrative Intelligence Briefs: LLM-Assisted Political Discourse Analysis in the Hungarian 2026 Pre-Election Context.* Proceedings of the 3rd Workshop on Natural Language Processing for Political Sciences (PoliticalNLP 2026) @ LREC 2026, pages 1–16. European Language Resources Association. DOI: 10.63317/228tnds8d6kd.

When discussing the implementation, also link the repository revision you inspected. The publication citation credits the study; it is not a claim that every published experiment can be reproduced from this snapshot.

## Reuse and contact

A code or prompt licence has not been specified in this repository. The publication's licensing information is available on the [publisher's page](https://lrec.elra.info/lrec2026-ws-politicalnlp-01); that is a separate publication record.

For research collaboration, reproduction questions or reuse enquiries, contact [hello@aletheos.team](mailto:hello@aletheos.team). Implementation issues can be reported through the repository's issue tracker.
