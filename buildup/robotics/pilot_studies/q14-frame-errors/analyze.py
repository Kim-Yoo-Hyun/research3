"""Post-observation diagnosis from preserved predictions; no fits or model imports."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--result", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=False)
    d = np.load(args.result/"inputs.npz")
    cfg = json.loads((args.result/"config.json").read_text())
    metrics = json.loads((args.result/"metrics.json").read_text())
    rows = [r for r in metrics["composition"] if r["condition"] == "noisy"]
    lookup = {(r["model"],r["scene"]):r for r in rows}
    geometry = []
    for scene in range(16):
        mask = (d["eval_scene"] == scene) & (d["eval_replica"] >= 0)
        theta = d["eval_theta"][mask][0]
        ee, base = d["eval_ee"][mask][0], d["eval_base"][mask][0]
        a = d["eval_action"][mask][0]
        c,s = np.cos(theta),np.sin(theta)
        q = np.array([c*ee[0]+s*ee[1],-s*ee[0]+c*ee[1]])
        jq, ja = np.array([-q[1],q[0]]), np.array([-a[1],a[0]])
        noise = d["eval_noise"][mask]
        delta_theta = -(noise[:,1]-noise[:,0])@jq / np.dot(ee,ee)
        delta_action = noise[:,2]-noise[:,1]
        projection = delta_action@ja
        first_order_gap = 2*(delta_theta.mean()*projection.mean()-(delta_theta*projection).mean())
        # Expected empirical-product gap includes 1/N original diagonal pairs.
        expected_gap = -(1-1/cfg["replicas"])*2*cfg["noise_sigma"]**2*np.dot(ee,base)/np.dot(ee,ee)
        measured = lookup[("geometry",scene)]["product_minus_paired"]
        geometry.append(dict(scene=scene, angle_deg=float(np.rad2deg(theta)),
                             radial_action_projection=float(np.dot(ee,base)/np.dot(ee,ee)),
                             measured_gap=measured, first_order_realized_gap=float(first_order_gap),
                             population_expected_gap=float(expected_gap),
                             linearization_abs_error=float(abs(measured-first_order_gap))))
    summary = []
    for model in ("geometry","joint_0","joint_1"):
        for angle in cfg["eval_angles_deg"]:
            rr = [r for r in rows if r["model"] == model and r["angle_deg"] == angle]
            m = float(np.mean([r["paired"]["mse"] for r in rr]))
            gap = float(np.mean([r["product_minus_paired"] for r in rr]))
            summary.append(dict(model=model,angle_deg=angle,
                paired_mse=m, signed_mean_gap=gap, signed_mean_gap_over_mse=gap/m,
                mean_absolute_scene_gap=float(np.mean([abs(r["product_minus_paired"]) for r in rr])),
                mean_g2=float(np.mean([r["paired"]["g2"] for r in rr])),
                mean_cross=float(np.mean([r["paired"]["cross"] for r in rr])),
                mean_bias_cross=float(np.mean([r["paired"]["bias_cross"] for r in rr])),
                mean_centered_cross=float(np.mean([r["paired"]["centered_cross"] for r in rr])),
                oracle_better_scenes=sum(r["oracle_mse"] < r["paired"]["mse"] for r in rr),
                sign_matches_geometry=int(sum(np.sign(r["product_minus_paired"]) == np.sign(lookup[("geometry",r["scene"])]["product_minus_paired"]) for r in rr)),
                noiseless_mse=float(np.mean([r["paired"]["mse"] for r in metrics["composition"] if r["model"]==model and r["angle_deg"]==angle and r["condition"]=="noiseless"]))))
    result=dict(purpose="post hoc explanation after first verified outputs; no new fits",
                geometry_derivation="delta_theta=-Jq dot (eta_E-eta_O)/||e||^2; delta_a=eta_G-eta_E; expected cross=2 sigma^2 e dot d/||e||^2; empirical product difference has -(1-1/N) factor",
                geometry_first_order=geometry,
                max_realized_linearization_error=max(r["linearization_abs_error"] for r in geometry),
                realized_first_order_sign_matches=int(sum(np.sign(r["measured_gap"])==np.sign(r["first_order_realized_gap"]) for r in geometry)),
                population_expected_sign_matches=int(sum(np.sign(r["measured_gap"])==np.sign(r["population_expected_gap"]) for r in geometry)),
                summaries=summary)
    (args.output/"diagnosis.json").write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (args.output/"scenes.csv").open('w') as f:
        fields=['model','scene','angle_deg','paired_mse','product_mse','oracle_mse','product_minus_paired','g2','a2','cross','bias_cross','centered_cross']
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader()
        for r in rows:
            writer.writerow(dict(model=r['model'],scene=r['scene'],angle_deg=r['angle_deg'],paired_mse=r['paired']['mse'],product_mse=r['product']['mse'],oracle_mse=r['oracle_mse'],product_minus_paired=r['product_minus_paired'],**{k:r['paired'][k] for k in fields[7:]}))
    print(json.dumps({k:v for k,v in result.items() if k!='geometry_first_order'},indent=2))


if __name__ == '__main__':
    main()
