SRCS_PY 	:= sut.py host.py params.py bridge_test.py\
                   ping_individual_test.py ping_individual_4_ports_test.py \
		   ping_bridges_test.py ping_bridges_4_ports_test.py \
		   traffic.py
PYLINT_OPTS     := --rcfile=./pylintrc --unsafe-load-any-extension=y

all: pep8 pylint

.PHONY: pep8
pep8: $(SRCS_PY)
	pep8 $^

.PHONY: pylint
pylint:  $(SRCS_PY)
	pylint ${PYLINT_OPTS} $(SRCS_PY)

.PHONY: clean
clean:
	rm -f *.pyc
