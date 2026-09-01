PYTHON ?= python3
QUARTO ?= quarto

.PHONY: all build prune-output clean-intermediate

all: build

build:
	$(PYTHON) scripts/generate_qr.py
	$(PYTHON) scripts/generate.py
	$(PYTHON) scripts/generate_audio.py
	$(PYTHON) scripts/generate.py
	$(QUARTO) render talk.qmd --output index.html
	$(MAKE) prune-output
	$(MAKE) clean-intermediate

# Quarto vendors development and alternate-module files that the rendered page
# does not load. Prune them after every render so the hosted artifact stays small.
prune-output:
	$(RM) talk_files/libs/revealjs/dist/reveal.js.map
	$(RM) talk_files/libs/revealjs/dist/reveal.esm.js
	$(RM) talk_files/libs/revealjs/dist/reveal.esm.js.map
	$(RM) -r talk_files/libs/revealjs/plugin/highlight
	$(RM) -r talk_files/libs/revealjs/plugin/markdown
	$(RM) -r talk_files/libs/revealjs/dist/theme/fonts/league-gothic
	$(RM) talk_files/libs/revealjs/plugin/math/math.esm.js
	$(RM) talk_files/libs/revealjs/plugin/math/plugin.js
	$(RM) talk_files/libs/revealjs/plugin/notes/notes.esm.js
	$(RM) talk_files/libs/revealjs/plugin/notes/plugin.js
	$(RM) talk_files/libs/revealjs/plugin/search/search.esm.js
	$(RM) talk_files/libs/revealjs/plugin/search/plugin.js
	$(RM) talk_files/libs/revealjs/plugin/zoom/zoom.esm.js
	$(RM) talk_files/libs/revealjs/plugin/zoom/plugin.js
	$(RM) talk_files/libs/revealjs/plugin/pdf-export/plugin.yml
	$(RM) talk_files/libs/revealjs/plugin/quarto-line-highlight/plugin.yml
	$(RM) talk_files/libs/revealjs/plugin/quarto-support/plugin.yml
	$(RM) talk_files/libs/revealjs/plugin/reveal-menu/plugin.yml

clean-intermediate:
	$(RM) talk.qmd audio/tts-manifest.json
	find scripts -type d -name __pycache__ -prune -exec $(RM) -r {} +
