#!/bin/bash

## init
token=$1
name=$(echo "$2" | sed "s/release-repo: //")
tag_ver="${name#?}"
tag_name="repository.betaseries/repository.betaseries-$tag_ver"
user="nekoserv-kodi-addons"
repo="betaseries"
create_release_url="https://api.github.com/repos/$user/$repo/releases"

## generate json data
generate_release_data() {
  cat <<EOF
{
  "tag_name": "$tag_name",
  "name": "$name"
}
EOF
}

post_data="$(generate_release_data)"
echo "Create release with: $post_data"

## create release and get id
release_id=$(curl \
  -so- \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token $token" \
  -d "$post_data" \
  "$create_release_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo "release_id is: $release_id"

## create archive
archive_name="repository.betaseries-$tag_ver.zip"
cd repository/; zip -qr ../$archive_name repository.betaseries; cd -

## add asset
add_asset_url="https://uploads.github.com/repos/$user/$repo/releases/$release_id/assets?name=$archive_name"
asset_id=$(curl \
  -so- \
  -H "Accept: application/vnd.github+json" \
  -H "Content-type: application/zip" \
  -H "Authorization: token $token" \
  --data-binary "@$archive_name" \
  "$add_asset_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo "asset_id is: $asset_id"