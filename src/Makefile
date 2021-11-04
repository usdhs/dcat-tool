DATE := $(shell date +%F)

clean:
	/bin/rm -rf *~ __pycache__ output.xlsx

run:
	FLASK_APP=hello flask run

check:
	pytest
	python dcat_tool.py --dump > /dev/null
	make template
	python dcat_tool.py --validate < tests/test_template_clean.json
	python dcat_tool.py --validate_lines < tests/test_template_clean.json
	python dcat_tool.py --validate_lines < tests/test_template_error_uid.json || exit 1

template:
	python dcat_tool.py --make_template ../dist/DIP_Template_output_$(DATE).xlsx
