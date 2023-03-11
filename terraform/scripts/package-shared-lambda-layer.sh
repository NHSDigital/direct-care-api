#!/bin/bash
CODEPIPELINE_BUCKET=$2-$1-utility-bucket

echo $CODEPIPELINE_BUCKET

REQUIREMENTS_CHANGED=0

# Create the dir
echo Creating python pacakges dir at ./build/lambdas/python/python/lib/python3.9/site-packages/
PACKAGES_DIR=./build/lambdas/python/python/lib/python3.9/site-packages/
mkdir -p $PACKAGES_DIR

# Generate dependency file
echo Creating requirements.txt from poetry
python -m poetry export -f requirements.txt --output $PACKAGES_DIR/requirements.txt

# Pull in the s3 requirements.txt file for comparison
echo Retrieving requirements.txt from S3 bucket
aws s3api get-object --bucket $CODEPIPELINE_BUCKET --key shared_layer/requirements.txt s3_requirements.txt

# Exit code 254 means requirements.txt doesn't exist - probably the first time doing this so just upload
# requirements.txt
if [ $(echo $?) = "254" ]; then
    echo No requirements.txt found in S3 bucket - adding current requirements.txt
    aws s3api put-object --bucket $CODEPIPELINE_BUCKET --key shared_layer/requirements.txt --body $PACKAGES_DIR/requirements.txt
    REQUIREMENTS_CHANGED=1
fi

echo Comparing local requirements.txt to S3 requirements.txt to see if shared_layer needs updating
cmp --silent s3_requirements.txt $PACKAGES_DIR/requirements.txt && echo "Requirements not changed" || REQUIREMENTS_CHANGED=1

if [ $(echo $REQUIREMENTS_CHANGED) = "1" ];
then
    echo local requirements.txt does not match S3 requirements.txt so shared_layer needs updating

    # Install dependencies (parent dir must be called 'python' or 'site-packages')
    echo Installing python packages to $PACKAGES_DIR
    python -m pip install -r $PACKAGES_DIR/requirements.txt --target $PACKAGES_DIR
    ( cd $PACKAGES_DIR && python -m pip install --upgrade --force-reinstall cffi)


    # Zip up the lambda layer for upload
    # -X option means don't add any metadata (which would cause shasum to change)
    # use touch to set the timestamps for all files to prevent shasum changing
    echo Zipping up $PACKAGES_DIR
    (cd ./build/lambdas/python && find . -exec touch -d '1985-10-21 09:00:00' {} \; && zip -i \* -rXq python.zip *)

    # Upload the new shared layer package to S3
    echo Uploading new python.zip shared layer to S3
    aws s3api put-object --bucket $CODEPIPELINE_BUCKET --key shared_layer/python.zip  --body ./build/lambdas/python/python.zip

    # Update the requirements file on s3
    echo Uploading new requirements.txt reference for shared_layer to S3
    aws s3api put-object --bucket $CODEPIPELINE_BUCKET --key shared_layer/requirements.txt --body $PACKAGES_DIR/requirements.txt
fi

rm -rf s3_requirements.txt
