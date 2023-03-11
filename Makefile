SHELL:=/bin/bash -O globstar
.SHELLFLAGS = -ecu


guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

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
	python -m flake8 lambdas/orchestration
	python -m pylint lambdas/orchestration --rcfile=tox.ini
	python -m mypy lambdas/orchestration
	cfn-lint template.yaml

integration-test: guard-BASE_URL
	echo "running integration tests"

clean:
	rm -rf .aws-sam || true
	find . -type d -name '.mypy_cache' | xargs rm -rf || true
	find . -type d -name '.pytest_cache' | xargs rm -rf || true
	find . -type d -name '__pycache__' | xargs rm -rf || true

sync: guard-stack_name
	sam sync --stack-name $$stack_name --region eu-west-2  --profile nhs-direct-care-dev

sync-watch: guard-stack_name
	sam sync --stack-name $$stack_name --region eu-west-2  --profile nhs-direct-care-dev --watch

delete-sam-stack: guard-stack_name
	sam delete --stack-name $$stack_name --region eu-west-2  --profile nhs-direct-care-dev

get-sam-endpoint: guard-stack_name
	@sam list endpoints --region eu-west-2  --profile nhs-direct-care-dev --stack-name=anthonydev --output json \
		| jq -r '.[] | select(.LogicalResourceId=="ServerlessRestApi") | .CloudEndpoint[] | select(. |endswith("directcareapi"))'

curl-sam: guard-sam_endpoint
	curl -s "$$sam_endpoint/calculate?a=5&b=7"

review-cloudformation-dev-resources:
	aws cloudformation deploy \
		--profile nhs-direct-care-dev \
		--template-file aws/cloudformation/dev_pipeline_resources.yaml \
		--stack-name aws-sam-cli-managed-dev-pipeline-resources \
		--parameter-overrides file://aws/cloudformation/dev_pipeline_resources_params.json \
		--capabilities CAPABILITY_IAM \
		--no-execute-changeset \
		--no-fail-on-empty-changeset

review-cloudformation-int-resources:
	aws cloudformation deploy \
		--profile nhs-direct-care-int \
		--template-file aws/cloudformation/int_pipeline_resources.yaml \
		--stack-name aws-sam-cli-managed-int-pipeline-resources \
		--parameter-overrides file://aws/cloudformation/int_pipeline_resources_params.json \
		--capabilities CAPABILITY_IAM \
		--no-execute-changeset \
		--no-fail-on-empty-changeset

review-cloudformation-pipeline-resources:
	aws cloudformation deploy \
		--profile nhs-direct-care-pipelines \
		--template-file aws/cloudformation/pipeline_resources.yaml \
		--stack-name github-managed-pipeline-resources \
		--parameter-overrides file://aws/cloudformation/pipeline_resources_params.json \
		--capabilities CAPABILITY_IAM \
		--no-execute-changeset \
		--no-fail-on-empty-changeset

deploy_pipeline: guard-CODEBUILD_TOKEN guard-CODEBUILD_USER guard-GIT_BRANCH
	./scripts/deploy_pipeline.sh

install-requirements:
	python -m pip install poetry
	python -m poetry export -f requirements.txt --output requirements.txt
	python -m pip install -r requirements.txt

pytest-ci:
	python -m pytest lambdas/orchestration --tb=short --capture=no -p no:warnings \
	--cov-report html --cov-report term --cov=lambdas/orchestration

prepare-terraform:
	unzip ./terraform/terraform-1.2.3 -d terraform

create-terraform-state-resources-%:
	aws s3api create-bucket --bucket dcapi-$*-utility-bucket --create-bucket-configuration LocationConstraint=eu-west-2
	cd terraform && terraform import 'aws_s3_bucket.utility_bucket' dcapi-dev-utility-bucket
	aws dynamodb create-table --table-name dcapi-$*-lock-table --attribute-definitions AttributeName=LockID,AttributeType=S \
	--key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST

DANGER-tf-init-dev:
	mkdir -p $$HOME/.terraform.d/plugin-cache
	cd terraform && terraform init -backend-config=env-config/dev.conf -reconfigure
	cd terraform && terraform workspace new dev || ./terraform workspace select dev && echo "dev workspace selected"

DANGER-tf-init-int:
	mkdir -p $$HOME/.terraform.d/plugin-cache
	cd terraform && terraform init -backend-config=env-config/int.conf -reconfigure
	cd terraform && terraform workspace new int || ./terraform workspace select int && echo "int workspace selected"

DANGER-tf-init-prod:
	mkdir -p $$HOME/.terraform.d/plugin-cache
	cd terraform && terraform init -backend-config=env-config/prod.conf -reconfigure
	cd terraform && terraform workspace new prod || ./terraform workspace select prod && echo "prod workspace selected"

switch-to-pr-%:
	if [ -z $* ]; then echo MUST SET PR NUMBER e.g. switch-to-pr-102 && exit 1; fi
	export PULL_REQUEST_NUMBER=$* && \
	cat ./terraform/env-config/pull-request-template.conf | envsubst > ./terraform/env-config/active-pr.conf
	cd terraform && terraform init -backend-config=env-config/active-pr.conf -reconfigure
	cd terraform && terraform workspace new pr-$* || terraform workspace select pr-$* && echo Switching to pr-$*
	aws s3api create-bucket --bucket dcapi-pr-$*-utility-bucket --create-bucket-configuration LocationConstraint=eu-west-2 || echo dcapi-pr-$*-utility-bucket already exists
	$(MAKE) package-lambdas env=pr-$*
	cd terraform && terraform import 'aws_s3_bucket.utility_bucket' dcapi-pr-$*-utility-bucket

tf-plan:
	# $(MAKE) package-lambdas
	cd terraform && terraform plan

tf-apply:
	cd terraform && terraform apply --auto-approve

tf-destroy-pr-%:
	$(MAKE) switch-to-pr-$*
	cd terraform && terraform apply -destroy --auto-approve

package-lambdas:
	bash terraform/scripts/package-lambdas-source-code.sh ${env}
	bash terraform/scripts/package-shared-lambda-layer.sh ${env}
