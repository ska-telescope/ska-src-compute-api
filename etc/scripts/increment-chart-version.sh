#!/bin/sh
# Increment the helm chart version.

var=`yq r ../helm/Chart.yaml version`
IFS=. read -r major minor patch <<EOF
$var
EOF

case "$1" in
patch) tag="$major.$minor.$((patch+1))"; ;;
major) tag="$((major+1)).0.0"; ;;
minor)     tag="$major.$((minor+1)).0"; ;;
esac

yq w -i ../helm/Chart.yaml version $tag

