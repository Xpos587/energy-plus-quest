# Native Scania branch: limited candidate, quality gate FAIL

Canonical frozen candidate: `scania-native-limited.blend`. Final render: `native-limitations-final.png` (1400×1050). This branch does not meet the requested illustrated reference quality. No other trucks, animation, game integration, or claim of final approval.

Source: Paolo, Scania R730, Printables 1396992, CC BY 4.0. [Attribution and download evidence](../sources/SOURCE-RECEIPT.md). The 9-page PDF is an automatic listing, not an exploded assembly guide. `import-sheet.png` inventories all64 source parts.

Actual curved source cab1, lower8, roof46, windowframe31, grilles10/11, mirrors33/47, seats39, six repeated clean tires2+rim18, fenders12/40, tanks14, headlamp housings30/62 are native mesh. Mixed print orientations were resolved visually. Approximate assembly, not a mechanically validated kit.

Source cab1 transform(x-55,50-y,z+42); lower8(x-53.2,27-z,y); roof46(x-54.3,50-z,y+53); frame31(x-53.35,-9-y,z+88), millimetres. Wheels at X±49,Y8/130/182,Z22.15. Source relief remains on cab doors: flattening damaged topology and replacement flush skins looked like flat plates. Both attempts were rejected; canonical limited model restores actual source curved shell and keeps the motif as an explicit reference mismatch.

Thin controlled chassis: two5×195×7mm rails atX±22,Y109,Z30 with four cross members. The archived detailed chassis experiment produced spikes and is excluded. Initial importer prefix glob could selectpart30 for3 or64 for6; this was an importer error, not proof of poor source files or print supports. Current rear tires are repeated clean part2; part3 not used.

Connected front fascia has green backing behind real grille and a slate gray radiator at(0,-50,77),86×1×49mm. Rear fender width reduced to approximately cab width. Headlamp depth flattened and recessed. These are geometry repairs; mechanical seams and material matching remain imperfect.

Interior uses parent-approved `../interior/two-drivers-v1.png`, packed in scene, on physical plane inside cab at(0,-32,119),86×56mm. Two source39 seats behind it. Wheel became visible after card was raised6mm. This is a planar illustrated interior, not volumetric humans; it looks more photographic than the claylike vehicle and remains a quality limitation. Clear glazing at(0,-55,116),92×52mm uses93%transparent/7%pale diffuse shader. No opaque gray plate.

Cycles CPU,48samples,denoise, Standard view,exposure0,gamma1; matte source materials and two broad area lights. Body linear(.18,.33,.22),roughness.88,specular.12. Grille(.21,.29,.30),tires(.18,.21,.21). Lights energy880000/480000,size250/210mm; worldstrength.65. No outlines. Parent owns separate final lookdev experiments.

Shape camera(-260,-340,235),target(0,37,87),ortho350mm,1400×1050. Front(0,-400,94),ortho205mm. Side(-500,72,94),ortho310mm. Map headings(-280,-330,370),(370,220,370),(-230,390,370),target(0,65,65),ortho390mm. Existing orthographic/map `v4` files belong to rejected intermediate door-skin candidates; they are not evidence for the canonical limited model. No verified game pixel sizing.

Remaining blockers: printed door motif differs from reference, interior card looks pasted, pale rims lack the desired visual depth, bare chassis looks too skeletal, cab/grille assembly still shows its kit nature, and material style does not reach the approved illustration. Render completion proves only artifact production, not user quality approval.
