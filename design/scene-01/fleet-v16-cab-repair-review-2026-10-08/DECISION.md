# Repair lower cab and zoom proof

User accepts mild vehicle shaking but rejects apparent camera shake and missing red front-wheel/cab cladding. Preserve accepted v16 appearance, smoke, routes and suspension amplitude.

Two separate causes were reproduced:

- Enlarged tracking export rounded crop coordinates to integer source pixels before 4× enlargement. This introduced visible stepping despite a fixed source camera. Replace with subpixel chassis-follow sampling and provide a genuinely fixed-world close-up.
- Original v16 lower side-cab faces had been clipped away; independent wheel/arch objects remained. Side diagnostics expose daylight above the front tire even before suspension was added. Repair lower cladding fit and maintain positive tire clearance throughout suspension travel.

Source candidate: `../fleet-v16-cab-repair-2026-10-08/`.
Prior proof: `../fleet-v16-worn-motion-2026-10-08/`.
No new cab model, full-scene restyling or production media replacement.
