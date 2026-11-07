# Reproducibility of this public companion

This note describes the companion snapshot based on revision `5aff7c2cf33b077043375c1bd85cbf955657e69e`. It records source inspection, not a completed reproduction run. The [paper](https://lrec.elra.info/lrec2026-ws-politicalnlp-01) remains the source for the study design, results and evaluation scope.

## Available and missing records

The repository contains exported prompts and their JSON configurations, contextual cards and Python processing modules. The article corpus, frozen analysis outputs, human evaluation annotations and a complete run manifest are not included in this public tree. The dependency requirements are not locked to a tested environment.

The study's source population and evaluation should be taken from the publication. The configurable source list and current defaults in the code are not a manifest of the exact corpus, models or prompts used in every published experiment. Reading the evaluation prompt does not reproduce either expert judgements or evaluation scores.

## Implementation limits visible in this snapshot

| Area | Source evidence and consequence |
| --- | --- |
| Entrypoint imports | [main.py](../src/political_nlp/main.py) refers to configuration and utility modules outside its package and imports pipeline modules from the package root rather than its `pipeline` directory. The old documented full-pipeline invocation needs integration repair and an import check before use. |
| JSON parsing | [data_io.py](../src/political_nlp/utils/data_io.py) uses Python `eval` for string values. That helper must not be used with untrusted input; replace it with an explicit data parser and verify the expected formats before adapting the pipeline. |
| Brief generation | [brief_generation.py](../src/political_nlp/pipeline/brief_generation.py) formats cluster statistics and a sample frame. It does not implement the full five-section, contextual-card-grounded brief described in the publication or automatically apply the exported brief prompt. |
| Prompt selection | Extraction modules can use local prompt constants or templates obtained from a configured Langfuse service. The exported prompt files are not automatically loaded as the local execution path. Bind a specific prompt revision before comparing results. |
| Collection limits | In [main.py](../src/political_nlp/main.py), `fetch_limit` truncates the collected DataFrame after article collection. It is not a limit on network fetches or an approved spend budget. |
| Error interpretation | [manipulation_detection.py](../src/political_nlp/pipeline/manipulation_detection.py) returns an empty technique list after an exception. An adapted workflow must preserve failure separately from a successful result with no technique found. |
| Dependencies and models | `requirements.txt` contains open version ranges and unpinned packages. Provider/model defaults and legacy SDK interfaces need a current compatibility review. No dependency installation, provider request or model download was performed for this documentation correction. |
| Python version | [rss_fetcher.py](../src/political_nlp/pipeline/rss_fetcher.py) imports `datetime.UTC`, introduced in Python 3.11. The former Python 3.9 prerequisite was insufficient for this source. |

These observations explain the scope of the published companion. They do not re-evaluate the paper or demonstrate that the study used these unresolved paths. No model, prompt, threshold, output or processing behaviour is changed by the handoff correction.

## Planning a reproduction or adaptation

Agree the research question, permitted inputs and the precise stage to reproduce. Then bind the source revision, environment, prompt/model choices and evaluation method; repair and test the chosen path offline before any external call. Keep request failures, empty results and excluded records distinct. External model execution and source collection have separate access, data-use and cost requirements.

For the study citation, see [CITATION.bib](../CITATION.bib). For collaboration and reuse enquiries, contact [hello@aletheos.team](mailto:hello@aletheos.team).
