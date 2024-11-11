#!/bin/bash

git clone https://github.com/danielmiessler/fabric

rm -rf prompts/fabric_patterns/*

cp -r fabric/patterns/* prompts/fabric_patterns/

rm -rf fabric