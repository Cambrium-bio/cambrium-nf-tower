config ?= compile

clean:
	./gradlew clean
	rm -rf .db
	docker rm nf-tower_db_1 || true

test:
ifndef class
	MICRONAUT_ENVIRONMENTS=mysql ./gradlew test
else
	MICRONAUT_ENVIRONMENTS=mysql ./gradlew test --tests ${class}
endif

build:
	./gradlew assemble
	./gradlew tower-backend:jibDockerBuild
	docker build -t tower-web:latest tower-web/

# Start nginx and FastAPI in addition to your normal services
run:
	docker-compose up -d
	# Example: Run FastAPI app if it's part of your stack
	# Uncomment if you need to start FastAPI (for example, if it's not part of Docker Compose)
	gunicorn -w 1 -b 0.0.0.0:8002 tower-submit.tower-submit:app

#run:
#	docker-compose up

deps:
	./gradlew -q tower-backend:dependencies --configuration ${config}

# Restart services including FastAPI
restart:
	docker-compose down
	make start
