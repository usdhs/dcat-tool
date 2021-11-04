DATE := $(shell date +%F)

clean:
	/bin/rm -rf *~ __pycache__ output.xlsx

check:
	pytest
	python dcat_tool.py --dump > /dev/null
	make template

template:
	python dcat_tool.py --make_template ../dist/DIP_Template_output_$(DATE).xlsx
