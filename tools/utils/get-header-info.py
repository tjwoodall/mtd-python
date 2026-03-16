#!/usr/bin/env python3

from __future__ import annotations

from typeguard import typechecked

from lxml import html
import sys

header_info = {}

@typechecked
def find_node(root:html.HtmlComment|html.HtmlElement, tag:str, attrib:str|None=None, value:str|None=None) -> list[html.HtmlElement]:
  rval = []
  if root.tag == tag:
    if attrib is None:
      rval.append(root)
    elif attrib in root.attrib:
      if value is None or root.attrib[attrib] == value:
        rval.append(root)

  for child in root:
    rval += find_node(child, tag, attrib, value)

  return rval

for f in sys.argv[1:]:
  tree = html.parse(f)

  root = tree.getroot()

  #Step 1. find the api information
  apis = find_node(root, "ol", "class", "govuk-list cmq-header-list--numbered")

  for api in apis:
#    print(html.tostring(api, pretty_print=True).decode())
    for headerdoc in api:
      header = find_node(headerdoc, "h3")
      if len(header) == 1:
        name = header[0].text
#        if name == "Gov-Client-Browser-JS-User-Agent":
#          print("HEADERDOC {{{")
#          print(html.tostring(headerdoc, pretty_print=True).decode())
#          print("HEADERDOC }}}")

#        print(html.tostring(header[0], pretty_print=True).decode())
        if name not in header_info:
          header_info[name] = {"name": name, "id": header[0].attrib['id'], "values": set(), "examples": set(), "description": "TBD"}
#        print(f"    {header[0].attrib['id']}:")
#        print(f"      name: {name}")
        this_header = header_info[name]
      else:
        print(f"UNEXPECTED: header.len = {len(header)}")
        continue

      v1 = find_node(headerdoc, "pre")
      for v1x in v1:
        v = find_node(v1x, "code")
        if len(v) != 1:
          print(f"UNEXPECTED - got {len(v)} looking for code, needed 1")
          continue

        if name == "Gov-Client-Connection-Method":
          this_header["values"].add(v[0].text.split(' ')[1])

        elif name in {"Gov-Client-Device-ID",
                      "Gov-Client-Local-IPs",
                      "Gov-Client-Local-IPs-Timestamp",
                      "Gov-Client-MAC-Addresses",
                      "Gov-Client-Multi-Factor",
                      "Gov-Client-Screens",
                      "Gov-Client-Timezone",
                      "Gov-Client-User-Agent",
                      "Gov-Client-User-IDs",
                      "Gov-Client-Window-Size",
                      "Gov-Vendor-License-IDs",
                      "Gov-Vendor-Product-Name",
                      "Gov-Vendor-Version",
                      "Gov-Client-Public-IP",
                      "Gov-Client-Public-IP-Timestamp",
                      "Gov-Client-Public-Port",
                      "Gov-Vendor-Forwarded",
                      "Gov-Vendor-Public-IP",
                      "Gov-Client-Browser-JS-User-Agent", }:
          for e in v:
            ex = e.text.split(' ', 1)
            if len(ex) == 2:
              this_header["examples"].add(ex[1])
            else:
              print(f"UNEXPECTED - can't find value for {name} header in {e.text}")
          p = find_node(headerdoc, "p")
          if len(p) >= 1:
            this_header["description"] = p[0].text

        else:
          printf("UNEXPECTED - unknown header {name}")

#    print(header[0].text)

#    links = find_node(api, "a", "href")
#
#    for link in links:
#        href = link.attrib["href"];
#        print(href) if href.startswith("/api-documentation/docs/api/service/") else ""

#      break
#    break


for k,v in header_info.items():
  print(f"    {v['id']}:")
  print(f"      name: {v['name']}")
  print(f"      description: {v['description']}")
  print(f"      in: header")
  print(f"      schema:")
  print(f"        type: string")
  if len(v['examples']) > 0:
    print(f"        example: \"{next(iter(v['examples']))}\"")
  if len(v['values']) > 0:
    print(f"        enum:")
    for l in v['values']:
      print(f"        - {l}")
  if len(v['examples']) > 0:
    print(f"      examples:")
    for idx, val in enumerate(v["examples"]):
      print(f"        name{idx}:")
      print(f"          value: \"{val}\"")

print()
print()

for k,v in header_info.items():
  print(f"      - $ref: '#/components/parameters/{v['id']}'")
