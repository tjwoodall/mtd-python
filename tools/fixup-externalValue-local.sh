#!/bin/bash

# Fixup value: $ref stuff which should be externalValue

# Some apis have public as the root, create a resources symlink for consistency
[[ -e resources ]] || ln -s . resources

p=resources/public/api/conf
[[ ! -h resources ]] || p=public/api/conf

for i in $( git grep -A1 " value:" ${p}/* | grep "\$ref" | cut -d- -f1 | sort -u ); do sed -ni "/value:/! { p }; /value:/ { N; s/value: *\r\?\n *\$ref:/externalValue:/; p }" $i; echo fixed $path/$i; done

for i in $( git grep -l "userRestricted:" ${p}/* ); do sed -i "s/userRestricted:/User-Restricted:/g" $i; echo fixed $path/$i; done
for i in $( git grep -l "applicationRestricted:" ${p}/* ); do sed -i "s/applicationRestricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done
for i in $( git grep -l "user-restricted:" ${p}/* ); do sed -i "s/user-restricted:/User-Restricted:/g" $i; echo fixed $path/$i; done
for i in $( git grep -l "application-restricted:" ${p}/* ); do sed -i "s/application-restricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done

exit 0

