#!/bin/bash

# index.html - the pages generated from webscrape
# github.html - the pages generate from hmrc github

iinfo="from the schemas at https://developer.service.hmrc.gov.uk/api-documentation/docs/api"
ginfo="from the github.com/hmrc/ repos"

header() {
cat <<EOF
<!DOCTYPE html>
<html>
<head>
<TITLE>Generated ${1}</TITLE>
  <style>
html, body {
  margin: 0;
  height: 100%;
}

body {
  display: flex;
  flex-direction: column;
}

header {
  padding: 10px 20px;
  border-bottom: 1px solid #ccc;
  flex-shrink: 0;
}

header h1 {
  margin: 10px 0;
}

.container {
  display: flex;
  flex: 1;
  min-height: 0;
}

nav {
  width: 250px;
  padding: 20px;
  box-sizing: border-box;
  border-right: 1px solid #ccc;
  overflow-y: auto;
}

main {
  flex: 1;
  min-width: 0;
}

iframe {
  width: 100%;
  height: 100%;
  border: 0;
}


  </style>
</head>

<body>
<header>
<a href="github.html">Documentation generated ${2}</a></br>

<h1>Documentation generated ${1}</h1></br>
</header>
<div class="container">
<nav>
EOF
}

header "${ginfo}" "${iinfo}" >github.html
header "${iinfo}" "${ginfo}" >index.html


for i in *.html; do
  case $i in
    index.html) ;;
    github.html) ;;
    *.webscrape.html)
      echo "<a href=\"$i\" target="documentation">${i%.webscrape.html}</a><br>" >>index.html
      [[ -s $ifirst ]] || ifirst=$i
      continue
    ;;
    *.html)
      echo "<a href=\"$i\" target="documentation">${i%.html}</a><br>" >>github.html
      [[ -s $gfirst ]] || gfirst=$i
      continue
    ;;
  esac
done

footer() {
cat <<EOF
  </nav>

  <main>
    <iframe name="documentation" src="${1}"></iframe>
  </main>
</div>
</body>
</html>
EOF
}

footer "$ifirst" >>index.html
footer "$gfirst" >>github.html

exit 0
