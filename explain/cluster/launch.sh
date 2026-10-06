#!/usr/bin/env bash
# Launch the pilot Job: explain/cluster/launch.sh smoke|pilot
# Ships the code as a ConfigMap owned by the Job, so both are cleaned up together.
set -euo pipefail
MODE=${1:?usage: launch.sh smoke|pilot}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
SUFFIX="$MODE-$(date -u +%m%d-%H%M%S)"
TMP=$(mktemp -d)
tar --exclude='__pycache__' -czf "$TMP/code.tgz" -C "$REPO" datagen utils models explain configs/explain eval
cp "$REPO/explain/cluster/run.sh" "$TMP/run.sh"
sed -e "s/JOBSUFFIX/$SUFFIX/g" -e "s/JOBMODE/$MODE/" "$REPO/explain/cluster/job.yaml" > "$TMP/job.yaml"
kubectl apply -f "$TMP/job.yaml" -l '!kueue.x-k8s.io/queue-name' 2>/dev/null || true   # the PVC
uid=$(kubectl apply -f "$TMP/job.yaml" -o jsonpath='{.items[1].metadata.uid}')
kubectl -n research create configmap "pfau-explain-code-$SUFFIX" \
  --from-file=code.tgz="$TMP/code.tgz" --from-file=run.sh="$TMP/run.sh"
kubectl -n research patch configmap "pfau-explain-code-$SUFFIX" --type=merge -p \
  "{\"metadata\":{\"ownerReferences\":[{\"apiVersion\":\"batch/v1\",\"kind\":\"Job\",\"name\":\"pfau-explain-$SUFFIX\",\"uid\":\"$uid\"}]}}"
rm -rf "$TMP"
echo "job/pfau-explain-$SUFFIX"
