#!/bin/bash

## init
token=$1
version=$(echo "$2" | sed "s/release: //")
tag_name="service.subtitles.betaseries"
user="nekoserv-kodi-addons"
repo="betaseries"
create_release_url="https://api.github.com/repos/$user/$repo/releases"

## remove previous tag
echo " -> Deleting previous tag"
curl \
  -s \
  -X DELETE \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$user/$repo/git/refs/tags/$tag_name"

## create release and get id
echo -n "\n -> Creating new release\n"
release_id=$(curl \
  -so- \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{"tag_name":"'$tag_name'","name":"betaseries '$version'"}' \
  "$create_release_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo -n "\n -> release_id is: $release_id\n"

## create archive
archive_name="$tag_name-${version#?}.zip"
cd ../; mv "$repo" "$tag_name";
zip -qr "$archive_name" "$tag_name" -x "*/.git*" "*/repository/*" "*/scripts/*"
mv "$tag_name" "$repo"

## add asset
add_asset_url="https://uploads.github.com/repos/$user/$repo/releases/$release_id/assets?name=$archive_name"
asset_id=$(curl \
  -so- \
  -H "Accept: application/vnd.github+json" \
  -H "Content-type: application/zip" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  --data-binary "@$archive_name" \
  "$add_asset_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo "\n -> asset_id is: $asset_id"
