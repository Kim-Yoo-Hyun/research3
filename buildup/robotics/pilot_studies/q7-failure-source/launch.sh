#!/usr/bin/env bash
set -u
cd /home/yoohyun/research3
stamp=$(date +%Y%m%d_%H%M%S)
owner=buildup/robotics/pilot_studies/q7-failure-source
cat >> "$owner/README.md" <<EOT

Launched download/build: \`$stamp\`; status \`launched\`.

\`\`\`bash
wget -c --timeout=30 --tries=3 -O datasets/q7-ur5/records.tar.gz https://huggingface.co/datasets/paulpacaud/ur5fail_test_dataset/resolve/fedfcb3346b92f6a2bfeb14dc254635c9a5013f1/records.tar.gz
docker build --pull --no-cache -t research3-q7-failure-source:v1 $owner
\`\`\`

Sessions: \`research3_q7_download_$stamp\`, \`research3_q7_build_$stamp\`.
Log/exit prefixes: \`logs/${stamp}_q7_download\`, \`logs/${stamp}_q7_build\`.
Expected input: archive bytes/hash above. Expected image: \`research3-q7-failure-source:v1\`.
EOT
tmux new-session -d -s "research3_q7_download_$stamp" "cd /home/yoohyun/research3 && wget -c --timeout=30 --tries=3 -O datasets/q7-ur5/records.tar.gz https://huggingface.co/datasets/paulpacaud/ur5fail_test_dataset/resolve/fedfcb3346b92f6a2bfeb14dc254635c9a5013f1/records.tar.gz > logs/${stamp}_q7_download.log 2>&1; printf '%s\\n' \$? > logs/${stamp}_q7_download.exit"
tmux new-session -d -s "research3_q7_build_$stamp" "cd /home/yoohyun/research3 && docker build --pull --no-cache -t research3-q7-failure-source:v1 $owner > logs/${stamp}_q7_build.log 2>&1; printf '%s\\n' \$? > logs/${stamp}_q7_build.exit"
printf '%s\n' "$stamp"
