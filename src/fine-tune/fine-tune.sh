#!/usr/bin/env bash

datetime=$(date '+%Y-%m-%d-%H-%M-%S')
display_name="devin-${datetime}"

firectl create fine-tuning-job --settings-file config.yml --display-name "${display_name}"
