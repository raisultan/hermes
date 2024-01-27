run-web:
	uvicorn hermes.web.main:app --reload

run-crawler:
	python3 hermes/crawler/main.py --path ./

clear-dbs:
	rm -rf storage.sqlite
	rm -rf volumes/
