# Wheel geometry candidate

`wheel_geometry.py` rebuilds `wheels-base.blend` from the accepted cab-repair source. It replaces visible wheel components with 48 consolidated manufactured wheel meshes, without changing vehicle root routes, hitches, cab vibration, smoke, crew, or camera.

Front tractor wheels use Ackermann angles from sampled route curvature and the front-to-rear-bogie wheelbase. All wheels roll by their individual signed world travel divided by world rolling radius. Trailer axles remain fixed in yaw. Blue's tractor route is straight throughout this source's 192 frames, so its front steering is correctly zero.

The common tyre profile uses local radius .358 and root scale 1.122. Axle beams and supports reach the existing chassis; tight radial ambient-contact patches sit at the virtual road plane. The render lane excludes these patches from the broad projected SUN shadow to avoid double counting.

Eight original trailer side guards are shortened only at their rear edges to root-local X=-4.0, clearing the first trailer tyre. Their transforms, parents and vertex counts remain unchanged. Existing hidden original wheel components are preserved for reversibility. Detailed cabin styling is untouched; the previously documented small lower cab cladding slit is not altered by this wheel work.

## Reproduction and evidence

Run Blender background on `wheel_geometry.py`, then `validate_wheels.py`. The canonical numerical results are in [wheel-validation.json](wheel-validation.json); object names, control definitions and distances are in [wheel-build-receipt.json](wheel-build-receipt.json). Validation reloads the saved blend and verifies persistent tyre/alloy/trim material slots, original animation preservation, all-frame road tangency, roll, steering and conservative wheel-arch clearance. This is an envelope check, not a full mesh collision simulation.

The initial consolidation incorrectly stored evaluated temporary material references, which reloaded as empty slots and produced white tyres. The corrected builder resolves every slot to its persistent original `bpy.data.materials` entry before saving. The saved-file validator rejects absent or incorrect slots.

This candidate covers the source's 192 frames at 24 fps. Longer route exports must rebake motion over their full frame range. Eight ventilation recesses, ten lug heads and an ordinary valve provide realistic rotation features, but numerical roll correctness alone does not prove freedom from 24 fps temporal aliasing; the render lane's adjacent-frame close-ups are the visual gate. No production asset is changed.
