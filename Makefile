project_name = direct-care-api

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

format:
	poetry run isort .
	poetry run black .

lint:
	python -m flake8 lambdas/orchestration
	python -m pylint lambdas/orchestration --rcfile=tox.ini
	python -m mypy lambdas/orchestration

integration-test: guard-BASE_URL
	echo "Running Integration Tests"
	python tests/integration/runner.py

install-requirements:
	python -m pip install poetry
	python -m poetry export --dev  -f requirements.txt --output requirements.txt
	python -m pip install -r requirements.txt

pytest-ci:
	python -m pytest lambdas/orchestration --tb=short --capture=no -p no:warnings \
	--cov-report html --cov-report term --cov=lambdas/orchestration

prepare-terraform:
	unzip ./terraform/terraform-1.2.3 -d terraform

create-terraform-state-resources-%:
	aws s3api create-bucket --bucket $(project_name)-$*-tf-bucket --create-bucket-configuration LocationConstraint=eu-west-2

	aws s3api create-bucket --bucket $(project_name)-$*-utility-bucket --create-bucket-configuration LocationConstraint=eu-west-2

	AWS_PAGER="" aws dynamodb create-table --table-name $(project_name)-$*-lock-table --attribute-definitions AttributeName=LockID,AttributeType=S \
		--key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST

	cd terraform && terraform init \
		-backend-config="key=$(project_name)-$*.tfstate" \
		-backend-config="bucket=$(project_name)-$*-tf-bucket" \
		-backend-config="dynamodb_table=$(project_name)-$*-lock-table" \
		-reconfigure

	$(MAKE) import-bucket-$*

DANGER-tf-init:
	mkdir -p $$HOME/.terraform.d/plugin-cache

	cd terraform && terraform init \
		-backend-config="key=$(project_name)-${env}.tfstate" \
		-backend-config="bucket=$(project_name)-${env}-tf-bucket" \
		-backend-config="dynamodb_table=$(project_name)-${env}-lock-table" \
		-reconfigure

	cd terraform && terraform workspace new ${env} || terraform workspace select ${env} && echo "${env} workspace selected"

switch-to-pr-%:
	if [ -z $* ]; then echo MUST SET PR NUMBER e.g. switch-to-pr-102 && exit 1; fi

	python -m pip install poetry

	cd terraform && terraform init \
		-backend-config="key=$(project_name)-pr-$*.tfstate" \
		-backend-config="bucket=$(project_name)-dev-tf-bucket" \
		-backend-config="dynamodb_table=$(project_name)-dev-lock-table" \
		-reconfigure

	cd terraform && terraform workspace new pr-$* || terraform workspace select pr-$* && echo Switching to pr-$*

	aws s3api create-bucket --bucket $(project_name)-pr-$*-utility-bucket --create-bucket-configuration LocationConstraint=eu-west-2 \
		|| echo $(project_name)-pr-$*-utility-bucket already exists

	$(MAKE) package-lambdas env=pr-$*

	$(MAKE) import-bucket-pr-$*

tf-plan:
	cd terraform && terraform plan -var "project-name=$(project_name)"

tf-apply:
	cd terraform && terraform apply -var "project-name=$(project_name)" --auto-approve

tf-destroy-pr-%:
	$(MAKE) switch-to-pr-$*
	cd terraform && terraform apply -destroy -var "project-name=$(project_name)" --auto-approve

package-lambdas:
	bash terraform/scripts/package-lambdas-source-code.sh
	bash terraform/scripts/package-shared-lambda-layer.sh ${env} $(project_name)

import-bucket-%:
	cd terraform && terraform import -var "project-name=$(project_name)" \
		'aws_s3_bucket.utility_bucket' $(project_name)-$*-utility-bucket \
		|| echo Resource already imported

zip-codebase-%:
	rm -rf $*-codebase-bundle.zip
	awk '{ print "\""$$0"\""}' ./.gitignore | xargs zip -r $*-codebase-bundle.zip . -x

tf-plan-with-output:
	cd terraform && ./terraform plan -out=tf_plan_commit_${version} -var "project-name=$(project_name)"

tf-apply-from-plan-output:
	cd terraform && ./terraform apply ${dir}/terraform/tf_plan_commit_${version}
