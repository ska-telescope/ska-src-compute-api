#!/bin/sh
# Increment the application version.

IFS=. read -r major minor patch < ../../VERSION

case "$1" in
patch) tag="$major.$minor.$((patch+1))"; ;;
major) tag="$((major+1)).0.0"; ;;
minor)     tag="$major.$((minor+1)).0"; ;;
esac

# Change the application VERSION
echo $tag > ../../VERSION

YQ_MAJ_VERSION=$(yq --version |  sed -r 's/^yq .*([1-9])\.[1-9]+\.[1-9]+.*/\1/')

case "$YQ_MAJ_VERSION" in
3) yq w -i ../helm/Chart.yaml appVersion $tag; ;;
4) yq -i ".appVersion = \"$tag\"" ../helm/Chart.yaml; ;;
esac
 
