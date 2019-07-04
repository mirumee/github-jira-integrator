#!/bin/bash
mkdir dist 
cp -rf ./*.py dist/
cp ./requirements.txt dist/
cd dist
pip3 install -r requirements.txt --target .
zip -r9 ../github-jira-sync.zip .
cd ..
aws lambda update-function-code --function-name github-jira-sync --zip-file fileb://github-jira-sync.zip
rm -rf dist github-jira-sync.zip
