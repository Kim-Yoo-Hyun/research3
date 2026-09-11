import io
import json
import unittest

import numpy as np

from probe import Fitter, fit_logistic, score_pair, select_pair, decide

PARAMS={'penalty':'l2','solver':'lbfgs','fit_intercept':True,'class_weight':None,
        'max_iter':2000,'tol':1e-8,'random_state':20260907,'C_grid':[.1,1.]}


class ProbeTests(unittest.TestCase):
    def test_imbalance_threshold_keeps_probability_score(self):
        y=np.array([False,True,True,True,True]); p=np.array([.70,.85,.90,.93,.95])
        ba_low,brier_low=score_pair(y,p,.5)
        ba_high,brier_high=score_pair(y,p,.8)
        self.assertEqual(ba_low,.5); self.assertEqual(ba_high,1.)
        self.assertEqual(brier_low,brier_high)

    def test_metric_ties_prefer_regularization_then_threshold(self):
        choices=[{'C':1.,'threshold':.5,'ba':.8,'brier':.1},
                 {'C':.1,'threshold':.8,'ba':.8-5e-13,'brier':.1+5e-13},
                 {'C':.1,'threshold':.6,'ba':.8,'brier':.1}]
        selected=select_pair(choices)
        self.assertEqual(selected['C'],.1); self.assertEqual(selected['threshold'],.6)

    def test_fitting_partition_scaler_and_numeric_replay(self):
        rows=[{'id':str(i),'recording_id':'a','success':i>=4,'features':{'f':float(i),'constant':7.}} for i in range(8)]
        record,scaler,model=fit_logistic(rows,['constant','f'],.1,PARAMS)
        self.assertEqual(record['mean'],[7.,3.5]); self.assertEqual(record['scale'][0],1.)
        holdout=np.array([[7.,1000.],[7.,-1000.]])
        z=(holdout-record['mean'])/record['scale']
        score=z@record['coef']+record['intercept']
        p=np.exp(-np.logaddexp(0,-score))
        np.testing.assert_allclose(p,model.predict_proba(scaler.transform(holdout))[:,1],atol=1e-12)
        self.assertEqual(record['mean'],[7.,3.5])

    def test_nested_tuning_excludes_each_validation_group(self):
        rows=[{'id':f'{g}:{i}','recording_id':g,'action':'pick','success':i%2==1,
               'features':{'duration':float(offset+i)}} for g,offset in [('a',0),('b',10),('c',1000)] for i in range(4)]
        protocol={'feature_groups':{'duration':['duration']},'model':PARAMS,
                  'threshold_grid':[.5,.8,.95],'metric_tie_tolerance':1e-12}
        models,inner,tuning=io.StringIO(),io.StringIO(),io.StringIO()
        fitter=Fitter(protocol,models,inner,tuning)
        fitter.tune(rows,['a','b','c'],'duration','pick','unmounted_outer')
        records=[json.loads(line) for line in models.getvalue().splitlines()]
        for record in records:
            expected=[r for r in rows if r['recording_id']!=record['inner']]
            self.assertEqual(record['fit_groups'],sorted({r['recording_id'] for r in expected}))
            self.assertAlmostEqual(record['mean'][0],np.mean([r['features']['duration'] for r in expected]))
            self.assertNotIn('unmounted_outer',record['fit_groups'])
        self.assertEqual(len(inner.getvalue().splitlines()),24)

    def test_decision_does_not_substitute_duration_augmented_score(self):
        protocol={'signal_support':{'min_gain_over_v5_prior_duration':.05,'min_primary_macro_ba':.75,'min_action_gain_over_v5':.05}}
        scores={}
        for m,ba in [('state_force',.7),('state',.7),('force',.5),('v5_selected',.72),('duration',.6),('v5_family_prior',.5),('state_force_duration',.99)]:
            scores[m]={'macro':{'balanced_accuracy':ba,'brier':.1},**{a:{'balanced_accuracy':ba} for a in ('pick','insert','remove')}}
        result=decide(scores,{'valid':1500,'intervals':{'gain_v5_selected':[-.1,.1]}},protocol)
        self.assertEqual(result['decision'],'NO_USEFUL_SUMMARY_GAIN')


if __name__=='__main__':
    unittest.main()
