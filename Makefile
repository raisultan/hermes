run-web:
	uvicorn hermes.web.main:app --reload

run-crawler:
	python3 hermes/crawler/main.py --path ./
