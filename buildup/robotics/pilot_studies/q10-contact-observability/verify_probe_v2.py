#!/usr/bin/env python3
"""Preserve the frozen verifier; correct only its log-loss clipping order."""
import json
import math
from pathlib import Path

import verify_probe as original

original_score = original.score


def score(rows):
    result = original_score(rows)
    loss = 0.
    for row in rows:
        # v5 clips p(success), then forms 1-p for failures. Clipping an already
        # complemented probability differs at the floating-point upper boundary.
        p = min(max(row['p'], 1e-12), 1-1e-12)
        loss -= math.log(p if row['success'] else 1-p)
    result['log_loss'] = loss / len(rows)
    return result


if __name__ == '__main__':
    revision = json.loads((original.ART/'verification_revision.json').read_text())
    assert original.sha(Path(__file__)) == revision['verifier_sha256']
    # Regression fixture for both clipped endpoints, using the frozen metric contract.
    from baselines import measure
    fixture = [{'success':False,'pred':True,'p':1.}, {'success':True,'pred':False,'p':0.}]
    original.close(score(fixture)['log_loss'], measure(fixture)['log_loss'])
    original.score = score
    original.main()
