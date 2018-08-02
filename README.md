# Concourse Email Resource
A [Concourse CI](http://concourse.ci) resource for watching emails in Gmail mailbox.

Uses https://github.com/charlierguo/gmail under the hood to connect to Gmail and retrieve emails over IMAP.

Useful for email-based approval workflows. 

Docker image: https://hub.docker.com/r/aptomi/concourse-gmail-resource

## Source Configuration
* `username`: *Required* Gmail username
* `password`: *Required* Gmail password

### Example
``` yaml
resource_types:
- name: gmail
  type: docker-image
  source:
    repository: aptomi/concourse-gmail-resource

resources:
- name: email-approvals
  type: gmail
  source:
    username: "test@gmail.com"
    password: "test"
```

## `get`: Get an email to be processed
No parameters.

## Development
To build the docker image for the resource:
``` sh
docker build -t <username>/concourse-gmail-resource .
```
