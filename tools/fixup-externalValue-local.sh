#!/bin/bash

# Fixup value: $ref stuff which should be externalValue

# Some apis have public as the root, create a resources symlink for consistency
[[ -e resources ]] || ln -s . resources

for i in $( git grep -A1 " value:" resources/public/api/conf/* | grep "\$ref" | cut -d- -f1 | sort -u ); do sed -ni "/value:/! { p }; /value:/ { N; s/value: *\r\?\n *\$ref:/externalValue:/; p }" $i; echo fixed $path/$i; done

for i in $( git grep -l "userRestricted:" resources/public/api/conf/* ); do sed -i "s/userRestricted:/User-Restricted:/g" $i; echo fixed $path/$i; done
for i in $( git grep -l "applicationRestricted:" resources/public/api/conf/* ); do sed -i "s/applicationRestricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done
for i in $( git grep -l "user-restricted:" resources/public/api/conf/* ); do sed -i "s/user-restricted:/User-Restricted:/g" $i; echo fixed $path/$i; done
for i in $( git grep -l "application-restricted:" resources/public/api/conf/* ); do sed -i "s/application-restricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done

exit 0

