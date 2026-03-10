# Sample Prompts

Use these as starting points. Keep user-provided requirements; do not invent new creative elements.

For inline prompting tips, see the "Prompting Best Practices" section of SKILL.md.

## Generate

### photorealistic-natural
```
Create an image of: a candid photo of an elderly sailor on a small fishing boat adjusting a net.
Scene/background: coastal water with soft haze.
Subject: weathered skin with wrinkles and sun texture; a calm dog on deck nearby.
Style: photorealistic candid photo, shot with a 50mm lens.
Composition: medium close-up, eye-level.
Lighting: soft coastal daylight, shallow depth of field, subtle film grain.
Constraints: natural color balance; no heavy retouching; no watermark.
```

### product-mockup
```
Create an image of: a premium product photo of a matte black shampoo bottle with a minimal label.
Scene/background: clean studio gradient from light gray to white.
Subject: single bottle centered with subtle reflection.
Style: premium product photography, softbox lighting.
Composition: centered, slight three-quarter angle, generous padding.
Constraints: no logos or trademarks; no watermark.
```

### ui-mockup
```
Create an image of: a mobile app UI for a local farmers market with vendors and specials.
Scene/background: clean white background with subtle natural accents.
Subject: header, vendor list with small photos, "Today's specials" section, location and hours.
Style: realistic product UI, not concept art.
Composition: iPhone frame, balanced spacing and hierarchy.
Constraints: practical layout, clear typography, no logos or trademarks, no watermark.
```

### infographic-diagram
```
Create an image of: a detailed infographic of an automatic coffee machine flow.
Scene/background: clean, light neutral background.
Subject: bean hopper -> grinder -> brew group -> boiler -> water tank -> drip tray.
Style: clean vector-like infographic with clear callouts and arrows.
Composition: vertical poster layout, top-to-bottom flow.
Text (verbatim): "Bean Hopper", "Grinder", "Brew Group", "Boiler", "Water Tank", "Drip Tray".
Constraints: clear labels, strong contrast, no logos, no watermark.
```

### logo-brand
```
Create an image of: an original logo for "Field & Flour", a local bakery.
Style: vector logo mark; flat colors; minimal.
Composition: single centered logo on plain background with padding.
Constraints: strong silhouette, balanced negative space; original design only; no gradients; no watermark.
```

### stylized-concept
```
Create an image of: a cavernous hangar interior with tall support beams and drifting fog.
Subject: compact shuttle, parked center-left, bay door open.
Style: cinematic concept art, industrial realism.
Composition: wide-angle, low-angle, cinematic framing.
Lighting: volumetric light rays cutting through fog.
Constraints: no logos or trademarks; no watermark.
```

### text-poster (Gemini strength)
```
Create an image of: a motivational poster for a gym.
Text (verbatim): "KEEP GOING" in bold white sans-serif, centered.
Background: dark blue gradient with subtle noise texture.
Style: modern typographic poster, clean layout.
Constraints: text must be legible and correctly spelled; no watermark.
```

### historical-scene
```
Create an image of: an outdoor crowd scene in Bethel, New York on August 16, 1969.
Scene/background: open field, temporary stages, period-accurate tents and signage.
Subject: crowd in period-accurate clothing, authentic staging and environment.
Style: photorealistic photo.
Composition: wide shot, eye-level.
Constraints: period-accurate details; no modern objects; no logos; no watermark.
```

## Asset Type Templates

### Website hero background
```
Create an image of: minimal abstract background with a soft gradient and subtle texture (calm, modern).
Style: matte illustration / soft-rendered abstract background.
Composition: wide composition; large negative space on the right for headline.
Lighting: gentle studio glow.
Color palette: cool neutrals with a restrained blue accent.
Aspect ratio: 16:9.
Constraints: no text; no logos; no watermark.
```

### Blog header image
```
Create an image of: overhead desk scene with notebook, pen, and coffee cup.
Scene/background: warm wooden tabletop.
Style: photorealistic photo.
Composition: wide crop; subject placed left; right side left empty.
Lighting: soft morning light.
Aspect ratio: 3:2.
Constraints: no text; no logos; no watermark.
```

### Social media card
```
Create an image of: [subject description].
Style: [photo/illustration].
Composition: centered, balanced for square crop.
Aspect ratio: 1:1.
Constraints: no text; no logos; no watermark.
```

### Extreme banner (Nano Banana 2)
```
Create an image of: [panoramic scene description].
Style: [photo/illustration].
Composition: wide panoramic, subjects spread across the frame.
Aspect ratio: 4:1.
Constraints: no text; no logos; no watermark.
```

## Edit

### text-localization (Gemini strength)
```
Translate all in-image text to Spanish.
Constraints: change only the text; preserve layout, typography, spacing, and hierarchy; no extra words; do not alter logos or imagery. Do not change the input aspect ratio.
```

### precise-object-edit
```
Replace ONLY the white chairs with wooden chairs.
Constraints: preserve camera angle, room lighting, floor shadows, and surrounding objects; keep all other aspects unchanged. Do not change the input aspect ratio.
```

### lighting-weather
```
Make it look like a winter evening with gentle snowfall.
Constraints: preserve subject identity, geometry, camera angle, and composition; change only lighting, atmosphere, and weather. Do not change the input aspect ratio.
```

### background-extraction
```
Extract the product on a transparent background.
Output: transparent background (RGBA PNG).
Constraints: crisp silhouette, no halos/fringing; preserve label text exactly; no restyling. Do not change the input aspect ratio.
```

### style-transfer
```
Apply the visual style from the reference image to this scene.
Constraints: preserve palette, texture, and brushwork from reference; no extra elements. Do not change the input aspect ratio.
```

### compositing (multi-image)
```
Place the subject from Image 2 next to the person in Image 1.
Constraints: match lighting, perspective, and scale; keep background and framing unchanged; no extra elements. Do not change the input aspect ratio.
```
