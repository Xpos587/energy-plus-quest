from pathlib import Path
import importlib.util
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v16compose',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.P=P
im=m.compose(144,P/'turn-vehicles/0144.png');im.save(P/'fit-map-0144.png');im.resize((960,667)).save(P/'fit-map-display-0144.png');im.crop((1280,150,1560,370)).resize((840,660)).save(P/'fit-user-region-0144.png')
