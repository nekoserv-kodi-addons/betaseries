#!/bin/bash

## init
token=$1
version=$(echo "$2" | sed "s/release: //")
tag_name="service.subtitles.betaseries"
user="nekoserv-kodi-addons"
repo="betaseries"
create_release_url="https://api.github.com/repos/$user/$repo/releases"

## remove previous tag
echo -n " -> Deleting previous tag : "
curl \
  -s \
  --fail \
  -X DELETE \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$user/$repo/git/refs/tags/$tag_name"
if [ $? -eq 0 ]; then echo "OK"; else echo "failed"; fi


echo -n " -> Finding previous release : "
release_id=$(curl \
  -so- \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/$user/$repo/releases/tags/$tag_name" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')

## remove previous release
if [ -z "$release_id" ]; then
	echo "KO (no previous release)"
else
	echo "OK"
	echo -n " -> Deleting release $release_id : "
	curl \
	  -s \
	  -X DELETE \
	  -H "Accept: application/vnd.github+json" \
	  -H "Authorization: Bearer $token" \
	  -H "X-GitHub-Api-Version: 2022-11-28" \
	  https://api.github.com/repos/$user/$repo/releases/$release_id
	echo "OK"
fi


## create release and get id
echo -n " -> Creating new release : "
release_id=$(curl \
  -so- \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{"tag_name":"'$tag_name'","name":"betaseries '$version'"}' \
  "$create_release_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo "$release_id"


## create archive
archive_name="$tag_name-${version#?}.zip"
cd ../; mv "$repo" "$tag_name";
zip -qr "$archive_name" "$tag_name" -x "*/.git*" "*/repository/*" "*/scripts/*" "*/betaseries/tests/*"
mv "$tag_name" "$repo"


## add archive asset
echo -n " -> asset_id #1 is : "
add_asset_url="https://uploads.github.com/repos/$user/$repo/releases/$release_id/assets?name=$archive_name"
asset_id=$(curl \
  -so- \
  -H "Accept: application/vnd.github+json" \
  -H "Content-type: application/zip" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  --data-binary "@$archive_name" \
  "$add_asset_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo "$asset_id"


## add icon asset
echo -n " -> asset_id #2 is : "
asset_name="resources/icon.png"
add_asset_url="https://uploads.github.com/repos/$user/$repo/releases/$release_id/assets?name=${asset_name##*/}"
asset_id=$(curl \
  -so- \
  -H "Accept: application/vnd.github+json" \
  -H "Content-type: application/zip" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  --data-binary "@$asset_name" \
  "$add_asset_url" | awk '/"id":/ {print; exit;}' | sed -E 's/^[^0-9]*([0-9]+).*/\1/')
echo "$asset_id"
