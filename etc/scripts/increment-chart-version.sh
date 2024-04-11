#!/bin/sh
# Increment the helm chart version.

YQ_MAJ_VERSION=$(yq --version |  sed -r 's/^yq .*([1-9])\.[1-9]+\.[1-9]+.*/\1/')

case "$YQ_MAJ_VERSION" in
3) var=`yq r ../helm/Chart.yaml version`; ;; 
4) var=`yq '.version' ../helm/Chart.yaml`; ;;
esac

echo $var

IFS=. read -r major minor patch <<EOF
$var
EOF

case "$1" in
patch) tag="$major.$minor.$((patch+1))"; ;;
major) tag="$((major+1)).0.0"; ;;
minor)     tag="$major.$((minor+1)).0"; ;;
esac

echo $tag

case "$YQ_MAJ_VERSION" in
3) yq w -i ../helm/Chart.yaml version $tag; ;;
4) yq -i ".version = \"$tag\"" ../helm/Chart.yaml; ;;
esac
