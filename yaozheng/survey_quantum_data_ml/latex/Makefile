# LaTeX survey report — build with xelatex (ctex) + bibtex
MAIN = main
BIB  = ../../quantum_data_ml_survey

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex preamble.tex chapters/*.tex $(BIB).bib
	xelatex -interaction=nonstopmode $(MAIN).tex
	bibtex $(MAIN)
	xelatex -interaction=nonstopmode $(MAIN).tex
	xelatex -interaction=nonstopmode $(MAIN).tex

quick: $(MAIN).tex preamble.tex chapters/*.tex
	xelatex -interaction=nonstopmode $(MAIN).tex

clean:
	rm -f $(MAIN).pdf $(MAIN).aux $(MAIN).log $(MAIN).out $(MAIN).toc $(MAIN).bbl $(MAIN).blg

.PHONY: all quick clean
