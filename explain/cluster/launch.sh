#!/usr/bin/env bash
# Launch the pilot Job: explain/cluster/launch.sh smoke|pilot
# Ships the code as a ConfigMap owned by the Job, so both are cleaned up together.
set -euo pipefail
MODE=${1:?usage: launch.sh smoke|pilot}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
# Runs only code that is on the fork (git@github.com:JacobPfau/queen.git), so
# every run is tied to a pushed commit.
cd "$REPO"
git fetch -q fork
COMMIT=$(git rev-parse HEAD)
git merge-base --is-ancestor "$COMMIT" fork/master || {
  echo "HEAD $COMMIT is not on fork/master; push it first" >&2; exit 1; }
SUFFIX="$MODE-$(date -u +%m%d-%H%M%S)"
TMP=$(mktemp -d)
git archive --format=tar.gz -o "$TMP/code.tgz" "$COMMIT" datagen utils models explain configs/explain eval
git show "$COMMIT:explain/cluster/run.sh" > "$TMP/run.sh"
git show "$COMMIT:explain/cluster/job.yaml" \
  | sed -e "s/JOBSUFFIX/$SUFFIX/g" -e "s/JOBMODE/$MODE/" -e "s/JOBCOMMIT/$COMMIT/" > "$TMP/job.yaml"
kubectl apply -f "$TMP/job.yaml" -l '!kueue.x-k8s.io/queue-name' 2>/dev/null || true   # the PVC
uid=$(kubectl apply -f "$TMP/job.yaml" -o jsonpath='{.items[1].metadata.uid}')
kubectl -n research create configmap "pfau-explain-code-$SUFFIX" \
  --from-file=code.tgz="$TMP/code.tgz" --from-file=run.sh="$TMP/run.sh"
kubectl -n research patch configmap "pfau-explain-code-$SUFFIX" --type=merge -p \
  "{\"metadata\":{\"ownerReferences\":[{\"apiVersion\":\"batch/v1\",\"kind\":\"Job\",\"name\":\"pfau-explain-$SUFFIX\",\"uid\":\"$uid\"}]}}"
rm -rf "$TMP"
echo "job/pfau-explain-$SUFFIX"
