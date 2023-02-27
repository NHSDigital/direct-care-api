#!/usr/bin/env bash

pull_request_id=$1
FeatureGitBranch=$2
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


cloudformation_exports=`aws cloudformation list-exports --profile nhs-direct-care-dev`

devPipelineExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:PipelineExecutionRole").Value'`
devCloudFormationExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:CloudFormationExecutionRole").Value'`
devArtifactsBucketARN=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:ArtifactsBucket").Value'`
arr_devArtifactsBucketARN=(${devArtifactsBucketARN//:/ })
devArtifactsBucket=${arr_devArtifactsBucketARN[3]}


cloudformation_exports=`aws cloudformation list-exports --profile nhs-direct-care-int`

intPipelineExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-int-pipeline-resources:PipelineExecutionRole").Value'`
intCloudFormationExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-int-pipeline-resources:CloudFormationExecutionRole").Value'`
intArtifactsBucketARN=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-int-pipeline-resources:ArtifactsBucket").Value'`
arr_intArtifactsBucketARN=(${intArtifactsBucketARN//:/ })
intArtifactsBucket=${arr_intArtifactsBucketARN[3]}

if [ -z "$pull_request_id" ]
then
      stackName=sam-app-pipeline
	  TestingStackName=direct-care-api-dev
	  ProdStackName=direct-care-api-int
else
      stackName=sam-app-pipeline-pr-${pull_request_id}
	  TestingStackName=direct-care-api-dev-pr-${pull_request_id}
	  ProdStackName=direct-care-api-int-pr-${pull_request_id}
fi

echo "devPipelineExecutionRole       : $devPipelineExecutionRole"
echo "devArtifactsBucket             : $devArtifactsBucket"
echo "devCloudFormationExecutionRole : $devCloudFormationExecutionRole"
echo "intPipelineExecutionRole       : $intPipelineExecutionRole"
echo "intArtifactsBucket             : $intArtifactsBucket"
echo "intCloudFormationExecutionRole : $intCloudFormationExecutionRole"
echo "CI stackName                   : $stackName"
echo "FeatureGitBranch               : $FeatureGitBranch"
echo "Testing StackName              : $TestingStackName"
echo "Prod StackName                 : $ProdStackName"


cp $SCRIPT_DIR/../resources/ci_pipeline_params_template.json /tmp/ci_pipeline_params.json
sed -i "s#@devPipelineExecutionRole#$devPipelineExecutionRole#g" /tmp/ci_pipeline_params.json
sed -i "s#@devArtifactsBucket#$devArtifactsBucket#g" /tmp/ci_pipeline_params.json
sed -i "s#@devCloudFormationExecutionRole#$devCloudFormationExecutionRole#g" /tmp/ci_pipeline_params.json
sed -i "s#@intPipelineExecutionRole#$intPipelineExecutionRole#g" /tmp/ci_pipeline_params.json
sed -i "s#@intArtifactsBucket#$intArtifactsBucket#g" /tmp/ci_pipeline_params.json
sed -i "s#@intCloudFormationExecutionRole#$intCloudFormationExecutionRole#g" /tmp/ci_pipeline_params.json
sed -i "s#@FeatureGitBranch#$FeatureGitBranch#g" /tmp/ci_pipeline_params.json
sed -i "s#@TestingStackName#$TestingStackName#g" /tmp/ci_pipeline_params.json
sed -i "s#@ProdStackName#$ProdStackName#g" /tmp/ci_pipeline_params.json

#aws cloudformation deploy \
#		--profile nhs-direct-care-pipelines \
#		--template-file ${SCRIPT_DIR}/../resources/ci_pipeline.yaml \
#		--stack-name ${stackName} \
#		--parameter-overrides file:///tmp/ci_pipeline_params.json \
#		--capabilities CAPABILITY_IAM \
#		--no-execute-changeset \
#		--no-fail-on-empty-changeset


#aws cloudformation deploy \
#		--profile nhs-direct-care-pipelines \
#		--template-file cloudformation/sam-app-pipeline.yaml \
#		--stack-name sam-app-pipeline \
#		--parameter-overrides file://cloudformation/sam-app-pipeline-params.json \
#		--capabilities CAPABILITY_IAM 
