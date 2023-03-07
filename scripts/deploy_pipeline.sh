#!/usr/bin/env bash
set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if test -z "$CODEBUILD_TOKEN"
then
	echo "\$CODEBUILD_TOKEN is empty"
	exit 1
fi

if test -z "$CODEBUILD_USER"
then
	echo "\$CODEBUILD_USER is empty"
	exit 1
fi

if test -z "$GIT_BRANCH"
then
	echo "\$GIT_BRANCH is empty"
	exit 1
fi



# leaving this in here as should use it but need permissions and roles sorting.....
# get dev information
#cloudformation_exports=`aws cloudformation list-exports --profile nhs-direct-care-dev`

#devPipelineExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:PipelineExecutionRole").Value'`
#devCloudFormationExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:CloudFormationExecutionRole").Value'`
#devArtifactsBucketARN=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-dev-pipeline-resources:ArtifactsBucket").Value'`
#arr_devArtifactsBucketARN=(${devArtifactsBucketARN//:/ })
#devArtifactsBucket=${arr_devArtifactsBucketARN[3]}

# get int information
#cloudformation_exports=`aws cloudformation list-exports --profile nhs-direct-care-int`

#intPipelineExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-int-pipeline-resources:PipelineExecutionRole").Value'`
#intCloudFormationExecutionRole=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-int-pipeline-resources:CloudFormationExecutionRole").Value'`
#intArtifactsBucketARN=`echo $cloudformation_exports | jq -r '.Exports[] |select(.Name=="aws-sam-cli-managed-int-pipeline-resources:ArtifactsBucket").Value'`
#arr_intArtifactsBucketARN=(${intArtifactsBucketARN//:/ })
#intArtifactsBucket=${arr_intArtifactsBucketARN[3]}

devPipelineExecutionRole=arn:aws:iam::436014718090:role/aws-sam-cli-managed-dev-pipe-PipelineExecutionRole-KWHOXSO2ZF0J
devArtifactsBucket=aws-sam-cli-managed-dev-pipeline-artifactsbucket-9cbzh2etlask
devCloudFormationExecutionRole=arn:aws:iam::436014718090:role/aws-sam-cli-managed-dev-p-CloudFormationExecutionR-HL4Z8GB0UI5U
intPipelineExecutionRole=arn:aws:iam::503308544674:role/aws-sam-cli-managed-int-pipe-PipelineExecutionRole-XBPVSUSWDGIC
intArtifactsBucket=aws-sam-cli-managed-int-pipeline-artifactsbucket-ja6wzylqqdr1
intCloudFormationExecutionRole=arn:aws:iam::503308544674:role/aws-sam-cli-managed-int-p-CloudFormationExecutionR-YHTLPPVNKT3V

if [ "$GIT_BRANCH" = "main" ]
then
      stackName=sam-app-pipeline
	  TestingStackName=direct-care-api-dev
	  IntStackName=direct-care-api-int
else
      stackName=sam-app-pipeline-pr-${PULL_REQUEST_ID}
	  TestingStackName=direct-care-api-dev-pr-${PULL_REQUEST_ID}
	  IntStackName=direct-care-api-int-pr-${PULL_REQUEST_ID}
fi

echo "devPipelineExecutionRole       : $devPipelineExecutionRole"
echo "devArtifactsBucket             : $devArtifactsBucket"
echo "devCloudFormationExecutionRole : $devCloudFormationExecutionRole"
echo "intPipelineExecutionRole       : $intPipelineExecutionRole"
echo "intArtifactsBucket             : $intArtifactsBucket"
echo "intCloudFormationExecutionRole : $intCloudFormationExecutionRole"
echo "CI stackName                   : $stackName"
echo "GIT_BRANCH                     : $GIT_BRANCH"
echo "Testing StackName              : $TestingStackName"
echo "Int StackName                  : $IntStackName"

# fix template params file for stack deployment
RENDERED_TEMPLATE=$SCRIPT_DIR/../rendered/ci_pipeline_params.json
mkdir -p $SCRIPT_DIR/../rendered/
cp $SCRIPT_DIR/../aws/cloudformation/ci_pipeline_params_template.json ${RENDERED_TEMPLATE}
sed -i "s#@devPipelineExecutionRole#$devPipelineExecutionRole#g" ${RENDERED_TEMPLATE}
sed -i "s#@devArtifactsBucket#$devArtifactsBucket#g" ${RENDERED_TEMPLATE}
sed -i "s#@devCloudFormationExecutionRole#$devCloudFormationExecutionRole#g" ${RENDERED_TEMPLATE}
sed -i "s#@intPipelineExecutionRole#$intPipelineExecutionRole#g" ${RENDERED_TEMPLATE}
sed -i "s#@intArtifactsBucket#$intArtifactsBucket#g" ${RENDERED_TEMPLATE}
sed -i "s#@intCloudFormationExecutionRole#$intCloudFormationExecutionRole#g" ${RENDERED_TEMPLATE}
sed -i "s#@FeatureGitBranch#$GIT_BRANCH#g" ${RENDERED_TEMPLATE}
sed -i "s#@TestingStackName#$TestingStackName#g" ${RENDERED_TEMPLATE}
sed -i "s#@IntStackName#$IntStackName#g" ${RENDERED_TEMPLATE}
sed -i "s#@IntStackName#$IntStackName#g" ${RENDERED_TEMPLATE}
sed -i "s#@CODEBUILD_TOKEN#$CODEBUILD_TOKEN#g" ${RENDERED_TEMPLATE}
sed -i "s#@CODEBUILD_USER#$CODEBUILD_USER#g" ${RENDERED_TEMPLATE}

#aws cloudformation deploy \
#		--profile nhs-direct-care-pipelines \
#		--template-file ${SCRIPT_DIR}/../resources/ci_pipeline.yaml \
#		--stack-name ${stackName} \
#		--parameter-overrides file:///tmp/ci_pipeline_params.json \
#		--capabilities CAPABILITY_IAM \
#		--no-execute-changeset \
#		--no-fail-on-empty-changeset

# check if stack exists
if aws cloudformation describe-stacks \
	--stack-name  ${stackName}  &>/dev/null
then
    echo 'stack exists'
	trigger_pipeline=1

else
	echo 'stack does not exist'
	trigger_pipeline=0
fi

aws cloudformation deploy \
		--template-file ${SCRIPT_DIR}/../aws/cloudformation/ci_pipeline.yaml \
		--stack-name ${stackName} \
		--parameter-overrides file://${RENDERED_TEMPLATE} \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset

cloudformation_exports=`aws cloudformation list-exports`
pipeline_name=`echo $cloudformation_exports | jq -r --arg stackName "$stackName:Pipeline"  '.Exports[] |select(.Name==$stackName).Value'`

if [ $trigger_pipeline -eq 1 ]; then
    echo "triggereing pipeline ${pipeline_name}"
	aws codepipeline start-pipeline-execution \
	--name ${pipeline_name}
fi
