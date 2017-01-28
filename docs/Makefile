PDF:=$(patsubst %.lyx,%.pdf,$(wildcard *.lyx))

all: $(PDF)

%.pdf: %.lyx
	lyx --export pdf $<

clean:
	rm *.pdf
