#!/bin/bash
CODEPIPELINE_BUCKET=dcapi-$1-pipeline-bucket

echo $CODEPIPELINE_BUCKET

REQUIREMENTS_CHANGED=0

# Create the dir
PACKAGES_DIR=./build/lambdas/python/python/lib/python3.9/site-packages/
mkdir -p $PACKAGES_DIR

# Generate dependency file
python -m poetry export -f requirements.txt --output $PACKAGES_DIR/requirements.txt

# Pull in the s3 requirements.txt file for comparison
aws s3api get-object --bucket $CODEPIPELINE_BUCKET --key requirements.txt s3_requirements.txt

# Exit code 254 means requirements.txt doesn't exist - probably the first time doing this so just upload
# requirements.txt
if [ $(echo $?) = "254" ]; then
    aws s3api put-object --bucket $CODEPIPELINE_BUCKET --key requirements.txt --body $PACKAGES_DIR/requirements.txt
    REQUIREMENTS_CHANGED=1
fi

cmp --silent s3_requirements.txt $PACKAGES_DIR/requirements.txt && echo "Requirements not changed" || REQUIREMENTS_CHANGED=1

if [ $(echo $REQUIREMENTS_CHANGED) = "1" ];
then
    # Install dependencies (parent dir must be called 'python' or 'site-packages')
    python -m pip install -r $PACKAGES_DIR/requirements.txt --target $PACKAGES_DIR

    # Lambdas come pre-installed with boto3 so can safely remove
    rm -rf $PACKAGES_DIR/site-packages/boto*/

    # Zip up the lambda layer for upload
    # -X option means don't add any metadata (which would cause shasum to change)
    # use touch to set the timestamps for all files to prevent shasum changing
    (cd ./build/lambdas/python && find . -exec touch -d '1985-10-21 09:00:00' {} \; && zip -i \* -rXq python.zip *)

    # Move the zipfile to the correct location
    aws s3api put-object --bucket $CODEPIPELINE_BUCKET --key python.zip  --body ./build/lambdas/python/python.zip

    # Update the requirements file on s3
    aws s3api put-object --bucket $CODEPIPELINE_BUCKET --key requirements.txt --body $PACKAGES_DIR/requirements.txt
fi

rm $PACKAGES_DIR/requirements.txt
rm s3_requirements.txt
