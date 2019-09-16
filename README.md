# snapshotalyzer-30000
Demo project to manage AWS EC2 instance snapshots

## About
This project is a demo, using boto3 to manage AWS EC2 instance snapshots.

## Configuring
shotty uses the configuration file created by the AWS cli for access control e.g.
'aws configure -- profile shotty'

## Running
'pipenv run python shotty/shotty.py <command> <subcommand> <--project=PROJECT>'

*command* is instances, volumes or snapshots list, start or stop
*subcommand* is:
       instances:  list, stop, start, snapshot
       volumes:  list
       snapshots:  list

*project* is optional
