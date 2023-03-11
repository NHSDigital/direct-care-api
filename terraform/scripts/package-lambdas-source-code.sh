#!/usr/bin/env bash


BASE_BUILD_DIR="./build/lambdas"

echo Removing old build dir
rm -rf ./build
echo Creating new build dir
mkdir -p $BASE_BUILD_DIR
echo Creating lambda_archives_dir
mkdir -p ./build/lambda_archives

lambdas=(
    "orchestration"
)


for value in ${lambdas[@]}
do
    echo Copying files for $value lambda to $BASE_BUILD_DIR/lambdas/${value}
    cp -r lambdas/${value} $BASE_BUILD_DIR

    # Zip up the source code to upload to the lambda
    # -X option means don't add any metadata (which would cause shasum to change)
    # use touch to set the timestamps for all files to prevent shasum changing
    echo Zipping up $value lambda files to $BASE_BUILD_DIR/lambdas/${value}.zip
    (cd $BASE_BUILD_DIR/${value} && find . -exec touch -d '1985-10-21 09:00:00' {} \; && zip -rqX ${value}.zip *)

     # Delete any directories that look like tests
    echo Deleting test files from $BASE_BUILD_DIR/${value}
    find $BASE_BUILD_DIR/${value} -type d -name "*tests*" | xargs rm -r

    # Move the zipfile to the correct location
    echo Moving zip archive from $BASE_BUILD_DIR/lambdas/${value}.zip to ./build/lambda_archives${value}.zip
    mv $BASE_BUILD_DIR/${value}/${value}.zip ./build/lambda_archives

done
