#!/bin/bash

for i in artifacts/*[0-9].json; do
  p=${i%.json}
  hj=$( jq --sort-keys . $p.json 2>/dev/null | md5sum )
  hr=$( jq --sort-keys . $p.redocly.json 2>/dev/null | sed 's/userRestricted/User-Restricted/' | md5sum )
  hw=$( jq --sort-keys . $p.webscrape.json 2>/dev/null | md5sum )

  if [[ "$hr" != "$hw" ]]; then
    if [[ "$hr" != "d41d8cd98f00b204e9800998ecf8427e  -" && "$hw" != "d41d8cd98f00b204e9800998ecf8427e  -" ]]; then
        echo $i
        echo "$hr - redocly"
        echo "$hw - webscrape"
        echo "vimdiff <( jq --sort-keys . $p.redocly.json ) <( jq --sort-keys . $p.webscrape.json )"
        diff $1 -u <( jq --sort-keys . $p.redocly.json ) <( jq --sort-keys . $p.webscrape.json )
    elif [[ "$hr" != "d41d8cd98f00b204e9800998ecf8427e  -" ]]; then
      echo $i
      echo "$hr - redocly"
      echo "missing - webscrape"
    else
      echo $i
      echo "missing - redocly"
      echo "$hw - webscrape"
    fi
    echo
  fi
  if [[ "$hj" != "$hw" ]]; then
    if [[ "$hj" != "d41d8cd98f00b204e9800998ecf8427e  -" && "$hw" != "d41d8cd98f00b204e9800998ecf8427e  -" ]]; then
      echo $i
      echo "$hj - json"
      echo "$hw - webscrape"
      echo "vimdiff <( jq --sort-keys . $p.json ) <( jq --sort-keys . $p.webscrape.json )"
      diff $1 -u <( jq --sort-keys . $p.json ) <( jq --sort-keys . $p.webscrape.json )
    elif [[ "$hj" != "d41d8cd98f00b204e9800998ecf8427e  -" ]]; then
      echo $i
      echo "$hj - json"
      echo "missing - webscrape"
    else
      echo $i
      echo "missing - json"
      echo "$hw - webscrape"
    fi
    echo
  fi

done

exit 0
