#!/usr/bin/env bash

BASE_BUILD_DIR="./build/lambdas"

rm -rf ./build
mkdir -p $BASE_BUILD_DIR
mkdir -p ./build/lambda_archives

lambdas=(
    "orchestration"
)

for value in ${lambdas[@]}
do

    # Create a dir for the lambda to live to mimic backend file structure
    MICROSERVICE_BUILD_DIR=$BASE_BUILD_DIR
    mkdir -p $MICROSERVICE_BUILD_DIR

    # Copy the relevant files for the microservice
    cp -r lambdas/${value} $MICROSERVICE_BUILD_DIR


    # Zip up the source code to upload to the lambda
    # -X option means don't add any metadata (which would cause shasum to change)
    # use touch to set the timestamps for all files to prevent shasum changing
    (cd $MICROSERVICE_BUILD_DIR/${value} && find . -exec touch -d '1985-10-21 09:00:00' {} \; && zip -rqX ${value}.zip *)

    # Move the zipfile to the correct location
    mv $MICROSERVICE_BUILD_DIR/${value}/${value}.zip ./build/lambda_archives

done

 # Delete any directories that look like tests
find $BASE_BUILD_DIR -type d -name "*tests*" | xargs rm -r
