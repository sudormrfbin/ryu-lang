dist:
	nuitka3 --onefile ryuc

parser:
	python3 -m lark.tools.standalone compiler/g.lark > compiler/lalr.py

test:
	pytest --maxfail 1 -vv

test-update:
	pytest --snapshot-update
