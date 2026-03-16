#!/bin/bash

fixup() {
  # Fixup value: $ref stuff which should be externalValue

  git submodule foreach 'git worktree add conflicts webscrape'

  git submodule foreach 'for i in $( git grep -A1 " value:" resources/public/api/conf/* | grep "\$ref" | cut -d- -f1 | sort -u ); do sed -ni "/value:/! { p }; /value:/ { N; s/value: *\r\?\n *\$ref:/externalValue:/; p }" $i; echo fixed $path/$i; done'

  git submodule foreach 'for i in $( git grep -l "userRestricted:" resources/public/api/conf/* ); do sed -i "s/userRestricted:/User-Restricted:/g" $i; echo fixed $path/$i; done'
  git submodule foreach 'for i in $( git grep -l "applicationRestricted:" resources/public/api/conf/* ); do sed -i "s/applicationRestricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done'
  git submodule foreach 'for i in $( git grep -l "user-restricted:" resources/public/api/conf/* ); do sed -i "s/user-restricted:/User-Restricted:/g" $i; echo fixed $path/$i; done'
  git submodule foreach 'for i in $( git grep -l "application-restricted:" resources/public/api/conf/* ); do sed -i "s/application-restricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done'

  git submodule foreach 'cd conflicts; for i in $( git grep -A1 " value:" resources/public/api/conf/* | grep "\$ref" | cut -d- -f1 | sort -u ); do sed -ni "/value:/! { p }; /value:/ { N; s/value: *\r\?\n *\$ref:/externalValue:/; p }" $i; echo fixed $path/$i; done'

  git submodule foreach 'cd conflicts; for i in $( git grep -l "userRestricted:" resources/public/api/conf/* ); do sed -i "s/userRestricted:/User-Restricted:/g" $i; echo fixed $path/$i; done'
  git submodule foreach 'cd conflicts; for i in $( git grep -l "applicationRestricted:" resources/public/api/conf/* ); do sed -i "s/applicationRestricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done'
  git submodule foreach 'cd conflicts; for i in $( git grep -l "user-restricted:" resources/public/api/conf/* ); do sed -i "s/user-restricted:/User-Restricted:/g" $i; echo fixed $path/$i; done'
  git submodule foreach 'cd conflicts; for i in $( git grep -l "application-restricted:" resources/public/api/conf/* ); do sed -i "s/application-restricted:/Application-Restricted:/g" $i; echo fixed $path/$i; done'
}

fixup

exit 0

# tools/fixup-externalValue.sh
# git submodule foreach 'git diff --color || true' | less
# git submodule foreach 'git commit -a -m "Replace value: \$ref with externalValue. Rename restricted keys for consistency" || true'
# git submodule foreach 'git checkout webscrape'
# tools/fixup-externalValue.sh
# git submodule foreach 'git diff --color || true' | less
# git submodule foreach 'git commit -a -m "Replace value: \$ref with externalValue. Rename restricted keys for consistency" || true'
# git submodule foreach 'git checkout main'

