import os
from pathlib import Path
os.environ['Q8_VERIFY_PREFIX']='cold'
exec(compile(Path('/work/verify.py').read_text(),'/work/verify.py','exec'))
