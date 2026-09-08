# Route and callout repair

The previous placement search switched preferred sides at the map midpoint and changed discrete candidates without temporal continuity. It also updated at the 18fps video rate. Labels now prefer the inside of their own route; their display positions use the browser animation clock, damped motion and a 140px/s speed ceiling. Tracking anchors remain tied to video time. A browser regression samples actual label speed.

Old trucks 1 and 4 used the upper edge of the lower street (mobile y=981), which included sidewalk and planting. Their lower route is moved to y=1018, preserving distinct speeds and complete trailer turns. Added 64px of existing city continuation below the video to avoid cropping the trucks. Desktop projection also extends beyond its former final interpolation knot instead of clamping new positions to the old edge. Generated videos and coordinate tracks were rebuilt together.

All 1152 frames: no truck collisions or viewport exits in either format. Desktop road envelope: no violations. Mobile retains four small envelope violations for unchanged truck 3 at the lower-left turn (maximum 4.54px squared); trucks 1 and 4 have none. This residual is not a claim of perfect road certification.

Sources checked: original July 23 scenario DOCX; July 30, August 12, August 24, September 2, September 4 and September 7 transcripts. The original scenario explicitly says carrier 2 immediately turns into the logistics centre after selection, in the result narrative. It also separately describes Express appearing at the doors. No instruction for truck 2 to enter the warehouse repeatedly during pre-choice movement was found. August 24 and September 4 require visually meaningful movement and relative proximity; September 7 clarifies the nearby warehouse. A separate post-selection arrival animation is not implemented by this route repair.

Validation: 17 unit tests; full existing browser suite 171 passed / 29 skipped; four focused inspection tests including the new continuous-motion check passed; static ZIP verifier passed after updating video dimensions to 720x1088 and 1280x788.
