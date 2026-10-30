"""Export verified 2x masters: python export.py WORKDIR OUTPUTDIR."""
from pathlib import Path
import sys
from PIL import Image

root, out = map(Path, sys.argv[1:3])
out.mkdir(parents=True, exist_ok=True)
for fmt, size in [('wide',(3884,1618)), ('tall',(1896,3318))]:
    for who in ['alva','khor','arseniy']:
        image = Image.open(root / f'final-{fmt}-{who}-2x.png')
        assert image.size == size
        path = out / f'choice-{fmt}-{who}.webp'
        image.save(path,'WEBP',quality=90,method=6)
        with Image.open(path) as check:
            assert check.format == 'WEBP' and check.size == size
        print(path.name,path.stat().st_size,flush=True)
