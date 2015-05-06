---
title: "Generating a coverage badge with Istanbul and S3"
tags:
- coffee-script
- development
- javascript
---

This is a quick shell script I whipped up to generate code-coverage badges for my private repos,
and upload them to S3.  Thought I'd share it here, in case anyone needs something similar.

<!--more-->

The basic idea is, we run Istanbul, we screen-scrape the coverage from the text summary,
we send this value to [shields.io](http://shields.io) to generate a pretty badge for us,
then we upload the resulting badge to S3.  Then we can link to the S3 image in GitHub's
README.md file, and see code coverage.

First, this requires that your project has `istanbul` installed and generates test coverage.  This
also requires [awscli](http://aws.amazon.com/cli/) for uploading badge images to S3, so in the
setup section on your build server:

    pip install awscli
    AWS_DEFAULT_REGION=us-east-1
    AWS_ACCESS_KEY_ID=xxxxx
    AWS_SECRET_ACCESS_KEY=xxxxx

Create a bucket named 'ci-badges' on S3, and then when we do the build:

    # Run tests and generate Istanbul coverage data
    npm test
    # Upload the results to S3
    S3_BUCKET=ci-badges makeBadge.sh myProject

This will make a badge for you at http://s3.amazonaws.com/ci-badges/myProject-master-coverage.svg

Here's the script:

    #!/bin/sh
    set -e

    # To use this script, install istanbul, generate code coverage data with coffee-coverage
    # or istanbul, and then:
    #
    #    makeBadge.sh [project-name]
    #

    # CI_BRANCH is provided by codeship.io.  Change if you're using some other build tool.
    GIT_BRANCH=${CI_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}

    # Adjust these as desired
    MED_COVERAGE=80
    HIGH_COVERAGE=90

    SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
    GIT_ROOT=$(git rev-parse --show-toplevel)
    ISTANBUL=${GIT_ROOT}/node_modules/.bin/istanbul

    if [ $# -ne 2 ]
    then
      echo "Syntax: $0 <bucket> <projectname>"
      exit 1
    fi

    S3_BUCKET=$1
    PROJECT_NAME=$2

    # Only generate badge for master.
    if [ "$GIT_BRANCH" != "master" ]; then
        # Only push stuff for 'master'
        echo "Not pushing because this branch is not master"
        exit 0
    fi

    floatLessThan () {
        echo "$1 $2" | awk '{if ($1 >= $2) exit 1; else exit 0}'
    }

    COVERAGE=$(${ISTANBUL} report text-summary | grep Statements | awk '{print $3+0}')
    echo "Coverage is ${COVERAGE}%"

    # Get a badge from shields.io
    if floatLessThan $COVERAGE $MED_COVERAGE; then
        COLOR=red
    elif floatLessThan $COVERAGE $HIGH_COVERAGE; then
        COLOR=yellow
    else
        COLOR=brightgreen
    fi
    curl -s -o "${GIT_ROOT}/coverage/badge.svg" \
        https://img.shields.io/badge/Code%20Coverage-${COVERAGE}%25-${COLOR}.svg
    echo "Generated badge coverage/badge.svg"

    # Upload badge to S3
    if command -v aws >/dev/null; then
        # Upload the badge to S3
        aws s3 cp ${GIT_ROOT}/coverage/badge.svg s3://${S3_BUCKET}/${PROJECT_NAME}-${GIT_BRANCH}-coverage.svg \
            --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
        echo "Wrote http://s3.amazonaws.com/${S3_BUCKET}/${PROJECT_NAME}-${GIT_BRANCH}-coverage.svg"
    else
        echo "aws not found.  Your badge isn't going anywhere..."
    fi
