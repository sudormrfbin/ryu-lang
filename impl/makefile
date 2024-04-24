dist:
	nuitka3 --onefile ryuc

parser:
	python3 -m lark.tools.standalone grammar.lark > compiler/lalr.py

t:
	pytest --maxfail 1 -vv

ut:
	pytest --snapshot-update
