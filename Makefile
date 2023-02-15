SHELL:=/bin/bash -O globstar
.SHELLFLAGS = -ecu

remove-docker-config:
	rm -f /home/vscode/.docker/config.json

install:
	poetry update && poetry install

build:
	sam build

start-api:
	mkdir -p logs
	local_endpoint_ip=$$(make -s local_endpoint_ip) && \
	echo "$$local_endpoint_ip" && \
	sam local start-api -d 9001 --warm-containers EAGER --parameter-overrides "ParameterKey=EndpointUrl,ParameterValue=http://$$local_endpoint_ip:3001" > logs/api.log 2>&1 &

curl:
	curl -s 'http://localhost:3000/calculate?a=5&b=7'

invoke:
	local_endpoint_ip=$$(make -s local_endpoint_ip) && \
	echo "$$local_endpoint_ip" && \
	echo '{"queryStringParameters": {"a":3, "b":4}}' | sam local invoke -d 9999 --parameter-overrides "ParameterKey=EndpointUrl,ParameterValue=http://$$local_endpoint_ip:3001" --event - MainFunction 

invoke-workers:
	local_endpoint_ip=$$(make -s local_endpoint_ip) && \
	echo "$$local_endpoint_ip" && \
	echo '{"a":3, "b":4}' | sam local invoke --event - AddFunction && \
	echo '{"a":3, "b":4}' | sam local invoke --event - MultiplyFunction && \
	echo '{"a":3, "b":4}' | sam local invoke --event - PowerFunction

start-lambda:
	# https://github.com/aws/aws-sam-cli/issues/510#issuecomment-860236830
	# https://whatibroke.com/2019/01/15/overriding-global-variables-aws-sam-local/
	# https://github.com/aws/aws-sam-cli/issues/2436
	mkdir -p logs
	sam local start-lambda -d 9000 --warm-containers EAGER --host 0.0.0.0  > logs/lambda.log 2>&1 &

stop-api:
	kill $$(ps -wwo pid,args | grep "[s]am local start-api" | awk '{print $$1}')

stop-lambda:
	kill $$(ps -wwo pid,args | grep "[s]am local start-lambda" | awk '{print $$1}')

stop-containers:
	CONTAINERS=$$(docker network inspect bridge | jq -r '.[].Containers[].Name'); echo "$$CONTAINERS" | xargs docker stop; echo "$$CONTAINERS" | xargs docker rm

up: build start-api start-lambda

down: stop-api stop-lambda stop-containers
	
local_endpoint_ip:
	@/sbin/ifconfig eth0 | grep 'inet ' | awk '{$$1=$$1};1' | cut -d' ' -f2

format:
	poetry run isort .
	poetry run black .

lint:
	poetry run pylint lambdas
	poetry run mypy lambdas
	poetry run cfn-lint template.yaml

test:
	mkdir -p reports
	poetry run pytest lambdas --junitxml=reports/junit.xml

clean:
	rm -rf .aws-sam || true
	find . -type d -name '.mypy_cache' | xargs rm -rf || true
	find . -type d -name '.pytest_cache' | xargs rm -rf || true
	find . -type d -name '__pycache__' | xargs rm -rf || true
