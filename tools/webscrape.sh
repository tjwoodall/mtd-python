#!/bin/bash

set -e

DOMAIN=https://developer.service.hmrc.gov.uk

declare -A scanned

if [[ $# -ne 3 ]]; then
  echo "Usage $0 <api> <version> <startpage>"
  echo "e.g.: $0 goods-movement-system-haulier-api 1.0 goods-movement-system-haulier-api/resources/public/api/conf"
  exit 1
fi

fatal()
{
  echo "$@"
  exit 1
}

# This is crude. but we don't want to parse the yaml/json at this point as some of it is invalid
# so we search for $ref"*: ["']*
do_download()
{
#  echo "do_download $*"
  local API=$1
  local VERSION=$2
  # readlink -f requires the directory to exist
  mkdir -p "${3%/*}"
  local target=$( readlink -f "$3" )

  [[ -z ${scanned[$target]} ]] || return 0
  scanned[$target]=1

#  echo "do_download $target"
  rm -f "${target}"
  w=${target#*/${VERSION}/}

  echo "Downloading ${target}"

  echo curl -s -o "${target}" "${DOMAIN}/api-documentation/docs/api/service/${API}/${VERSION}/oas/${w}"
  code=$( curl -s -o "${target}" -w "%{http_code} %{redirect_url}" "${DOMAIN}/api-documentation/docs/api/service/${API}/${VERSION}/oas/${w}" )
  [[ $code =~ ^200 ]] || fatal "curl returned $code"

  grep '\$ref' "$target" | sed -e 's/.*\$ref"\{0,1\}: *["'"'"']\{0,1\}\([^"'"'"']*\).*/\1/' -e 's/#.*//' | sort -u | grep -v '^$' | while read b; do
#    echo "b='$b'"
    p=${target%/*}/${b}
#    echo "p=$p"
    do_download "$API" "$VERSION" "${p}"
  done

  grep externalValue "$target" | sed -e 's/.*externalValue"\{0,1\}: *["'"'"']\{0,1\}\([^"'"'"']*\).*/\1/' -e 's/#.*//' | sort -u | while read b; do
    p=${DOMAIN}/api-documentation/docs/api/service/${API}/${VERSION}/oas/${b}
    w=${target%/${VERSION}/*}/${VERSION}/${b}
    mkdir -p "${w%/*}"
    echo curl -s -o "${w}" "${p}"
    code=$( curl -s -o "${w}" -w "%{http_code} %{redirect_url}" "${p}" )
    [[ $code =~ ^200 ]] || fatal "curl returned $code"
  done
}

rm -fr "${3}/${2}"
do_download "$1" "$2" "$3/$2/application.yaml"

exit 0
