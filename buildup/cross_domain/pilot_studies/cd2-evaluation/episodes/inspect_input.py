"""Container-only structural inspection; never execute on the host."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

source = Path('/input/nscore/data/LBM/lbm_data.pkl')
data = pd.read_pickle(source)
df = data['figure_4_hardware_tasks'].reset_index()
rows = []
for _, r in df.iterrows():
    rows.append({str(k): {'shape': list(v.shape), 'dtype': str(v.dtype)}
                 if isinstance(v, np.ndarray) else
                 {'length': len(v), 'type': type(v).__name__} if isinstance(v, (list, tuple)) else
                 v.item() if isinstance(v, np.generic) else v
                 for k, v in r.items()})
report = {'keys': list(data), 'columns': list(df.columns), 'rows': rows,
          'versions': {'numpy': np.__version__, 'pandas': pd.__version__}}
Path('/output/schema.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
