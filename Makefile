DATE := $(shell date +%F)

check:
	pytest
	make template

template:
	python src/dcat_tool.py --make_template dist/DIP_Template_output_$(DATE).xlsx
