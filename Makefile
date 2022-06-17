build:
	docker-compose up --build -d

clean:
	docker-compose down
# 	docker system prune -fa

single:
	cd ./api; \
	docker image build -t flaskapp .; \
	docker run -p 8000:8000 -d flaskapp
	cd ..