#!/bin/bash

set -euo pipefail

BRANCH=artifacts
TMP_INDEX=$(mktemp)

trap 'rm -f "${TMP_INDEX}"' EXIT

REPO_ROOT="$(git rev-parse --show-toplevel)"
ARTIFACTS_DIR="${REPO_ROOT}/artifacts"

# Start with an empty index.
GIT_INDEX_FILE="${TMP_INDEX}" git read-tree --empty

# Add the contents of artifacts/ to the temporary index,
# stripping the leading "artifacts/" directory.
while IFS= read -r -d '' file; do
  path="${file#"${ARTIFACTS_DIR}"/}"

  hash=$(git hash-object -w "${file}")

  GIT_INDEX_FILE="${TMP_INDEX}" git update-index \
    --add \
    --cacheinfo 100644 "${hash}" "${path}"
done < <(
  find "${ARTIFACTS_DIR}" \
    -type f \
    \( \
      -path "${ARTIFACTS_DIR}/docs/*" -print0 \
      -o -path "${ARTIFACTS_DIR}/cache/*" -o -name '*.redocly.json' -o -name '*.extraconfig.json' -o -name '*.config.json' -o -name '*.json' -print0 \
    \)
)

TREE=$(GIT_INDEX_FILE="${TMP_INDEX}" git write-tree)

if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    CURRENT_TREE=$(git rev-parse "${BRANCH}^{tree}")

    if [[ "${TREE}" == "${CURRENT_TREE}" ]]; then
        echo "Artifacts unchanged; nothing to commit."
        exit 0
    fi

    PARENT=(-p "$(git rev-parse "${BRANCH}")")
else
    PARENT=()
fi

COMMIT=$(git commit-tree "${TREE}" "${PARENT[@]}" -m "Update artifacts at $(date)")
git update-ref "refs/heads/${BRANCH}" "${COMMIT}"

echo "Saved artifacts to ${BRANCH}: ${COMMIT}"
