#!/bin/bash

token=$1
ver=$(echo "$2" | sed "s/release: //")
user="nekoserv-kodi-addons"
repo="betaseries"
tag_ver="${ver#?}"
tag="repository.betaseries/repository.betaseries-$tag_ver"
api="https://api.github.com/repos/$user/$repo/releases"

generate_release_data()
{
  cat <<EOF
{
  "tag_name": "$tag",
  "name": "$ver"
}
EOF
}

post_data="$(generate_release_data)"

echo "Create release"
echo "$post_data"

curl \
    -X POST \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: token $token" \
    --data "$post_data" \
    "$api"
