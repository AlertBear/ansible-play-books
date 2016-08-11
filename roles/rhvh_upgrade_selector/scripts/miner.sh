#!/bin/bash

die() {
    echo "Usage $0 [date]"
    echo "e.g.: $0 20160810.1"
}

REPO_PATH="/var/www/builds/rhvhupgrade/rhvh/4/os/Packages"
UPDATE_RPMS_PATH="/var/www/builds/rhvhupgrade/updates"
RPM_LINK_NAME="redhat-virtualization-host-image-update-latest.rpm"


if [[ $# != 1 ]]; then
    die
    exit 1;
fi

update_rpm=$(find $UPDATE_RPMS_PATH -name "*$1*" -print)
if [[ -z "$update_rpm" ]]; then
    echo "Can not find rpm name match '$1'"
    exit 1;
fi

pushd $REPO_PATH
ln -sf $update_rpm "$REPO_PATH/$RPM_LINK_NAME"
rm -rf repodata && createrepo .
popd
