#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


cloudformation_exports=`aws cloudformation list-exports --profile nhs-direct-care-dev`


devPipelineExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:PipelineExecutionRole").Value'`
devArtifactsBucket=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:ArtifactsBucket").Value'`
devCloudFormationExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:CloudFormationExecutionRole").Value'`

echo "devPipelineExecutionRole       : $devPipelineExecutionRole"
echo "devArtifactsBucket             : $devArtifactsBucket"
echo "devCloudFormationExecutionRole : $devCloudFormationExecutionRole"


cp $SCRIPT_DIR/../resources/ci_pipeline_params_template.json /tmp/ci_pipeline_params.json
sed -i "s#@devPipelineExecutionRole#$devPipelineExecutionRole#g" /tmp/ci_pipeline_params.json
sed -i "s#@devArtifactsBucket#$devArtifactsBucket#g" /tmp/ci_pipeline_params.json
sed -i "s#@devCloudFormationExecutionRole#$devCloudFormationExecutionRole#g" /tmp/ci_pipeline_params.json

aws cloudformation deploy \
		--profile nhs-direct-care-pipelines \
		--template-file ${SCRIPT_DIR}/../resources/ci_pipeline.yaml \
		--stack-name sam-app-pipeline \
		--parameter-overrides file:///tmp/ci_pipeline_params.json \
		--capabilities CAPABILITY_IAM \
		--no-execute-changeset \
		--no-fail-on-empty-changeset


#aws cloudformation deploy \
#		--profile nhs-direct-care-pipelines \
#		--template-file cloudformation/sam-app-pipeline.yaml \
#		--stack-name sam-app-pipeline \
#		--parameter-overrides file://cloudformation/sam-app-pipeline-params.json \
#		--capabilities CAPABILITY_IAM 
