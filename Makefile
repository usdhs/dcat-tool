DATE := $(shell date +%F)

template:
	python src/dcat_tool.py --make_template dist/DIP_Template_output_$(DATE).xlsx
