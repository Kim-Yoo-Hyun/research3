#!/bin/sh
set -eu
cd /home/yoohyun/research3
entry=buildup/robotics/pilot_studies/q1-predicate-stability/run.sh
Q1_NETWORK=bridge sh "$entry" smoke.py > logs/20260908_q1_smoke.log 2>&1
sh "$entry" evaluate.py pd_ee_delta_pos > logs/20260908_q1_ee.log 2>&1
sh "$entry" evaluate.py pd_joint_delta_pos > logs/20260908_q1_joint.log 2>&1
sh "$entry" relabel.py > logs/20260908_q1_relabel.log 2>&1
sh "$entry" verify.py > logs/20260908_q1_verify.log 2>&1
