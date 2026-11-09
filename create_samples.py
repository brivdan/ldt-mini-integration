from pathlib import Path
from ldt_demo import encode_field

ROOT = Path(__file__).parent / 'samples'
ROOT.mkdir(exist_ok=True)

def write(name, items):
    (ROOT / name).write_bytes(b''.join(encode_field(*item) for item in items))

patient = [('3101','Mustermann'), ('3102','Max'), ('3103','01011985')]
observation = [('8410','GLUC'), ('8411','Glucose'), ('8420','120'), ('8421','mg/dL')]
write('ldt2_demo.ldt', [('8000','8205'), *patient, *observation])
write('ldt3_demo.ldt', [
    ('8000','8205'),
    ('8002','Obj_0047'), *patient, ('8003','Obj_0047'),
    ('8002','Obj_0060'), *observation, ('8003','Obj_0060'),
])
print('Created synthetic learning examples in samples/')
