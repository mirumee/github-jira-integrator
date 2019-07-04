#!/bin/bash
mkdir dist 
cp -rf ./*.py dist/
cp ./requirements.txt dist/
cd dist
pip3 install -r requirements.txt --target .
zip -r9 ../github-jira-integration.zip .
cd ..
aws lambda update-function-code --function-name github-jira-integration --zip-file fileb://github-jira-integration.zip
rm -rf dist github-jira-integration.zip
