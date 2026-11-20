# Example: Acme Coffee

Acme Coffee is an invented small roaster. It sells a wholesale bean subscription to independent cafes and wants a lead magnet for cafe owners. Every name and number here is made up for the example.

| File | Made by | What it is |
|---|---|---|
| `input-voice-note.md` | the owner | The raw input: a voice note transcript |
| `survey/responses.csv` | the owner | 24 invented survey answers |
| `survey/outline.md` | `cluster_survey.py` | Themes, quotes and a suggested format |
| `concepts.json` | the model (`magnet-concept`) | 4 concepts scored on the five tests |
| `concept.md` | the model | The winning concept card |
| `magnet.md` | the model (`magnet-writer`) | The checklist, source of truth |
| `magnet.html` | `md_to_html.py` | The standalone page |
| `magnet.notion.json` | `md_to_notion.py` (dry run) | What would be sent to Notion |
| `flow.json` | the model (`keyword-delivery`) | The delivery flow config |
| `flow.md` | `flow_builder.py` | The setup sheet and test plan |
| `promo.md` | the model (`magnet-promo`) | Promo posts per platform |

Rebuild the generated files from the repo root:

```
python3 skills/survey-to-magnet/scripts/cluster_survey.py examples/acme-coffee/survey/responses.csv --segment stage -o examples/acme-coffee/survey/outline.md
python3 skills/magnet-concept/scripts/score_concepts.py examples/acme-coffee/concepts.json
python3 skills/magnet-writer/scripts/magnet_lint.py examples/acme-coffee/magnet.md --format checklist --keyword DIALIN
python3 skills/magnet-writer/scripts/md_to_html.py examples/acme-coffee/magnet.md -o examples/acme-coffee/magnet.html --accent "#2f6f4f"
python3 skills/magnet-writer/scripts/md_to_notion.py examples/acme-coffee/magnet.md -o examples/acme-coffee/magnet.notion.json
python3 skills/keyword-delivery/scripts/flow_builder.py examples/acme-coffee/flow.json -o examples/acme-coffee/flow.md
python3 skills/magnet-promo/scripts/promo_check.py examples/acme-coffee/promo.md --keyword DIALIN
```
