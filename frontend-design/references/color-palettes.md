# Color Palettes by Mood

Ready-to-use palettes with CSS custom properties. Each palette: 5 core colors + suggested usage.

---

## Dark & Moody

### Obsidian Night
Deep blacks with electric accent. For: dashboards, dev tools, luxury dark UIs.
```css
:root {
  --color-bg:      #0a0a0b;
  --color-surface:  #16161a;
  --color-text:     #e2e2e6;
  --color-muted:    #72727e;
  --color-accent:   #7f5af0;
}
```

### Deep Sea
Near-black blues with bioluminescent green. For: data viz, monitoring, analytics.
```css
:root {
  --color-bg:      #020d1a;
  --color-surface:  #0a1f33;
  --color-text:     #c5dbe6;
  --color-muted:    #4a6d80;
  --color-accent:   #00ffc8;
}
```

### Charcoal Ember
Warm dark with amber glow. For: media players, reading apps, content platforms.
```css
:root {
  --color-bg:      #1a1410;
  --color-surface:  #2a2118;
  --color-text:     #e8ddd0;
  --color-muted:    #8c7a6b;
  --color-accent:   #e07a2f;
}
```

---

## Light & Clean

### Paper White
Off-white with ink-black and a single warm accent. For: text-heavy, editorial, documentation.
```css
:root {
  --color-bg:      #faf9f6;
  --color-surface:  #ffffff;
  --color-text:     #1a1a1a;
  --color-muted:    #8b8b8b;
  --color-accent:   #c44d2b;
}
```

### Morning Fog
Cool gray base with blue accent. For: professional tools, B2B, productivity.
```css
:root {
  --color-bg:      #f0f2f5;
  --color-surface:  #ffffff;
  --color-text:     #1d2939;
  --color-muted:    #667085;
  --color-accent:   #1570ef;
}
```

### Cream Canvas
Warm off-white with olive green. For: portfolios, blogs, organic brands.
```css
:root {
  --color-bg:      #f5f0e8;
  --color-surface:  #fffdf7;
  --color-text:     #2c2c2c;
  --color-muted:    #8a8578;
  --color-accent:   #4a6741;
}
```

---

## Bold & Energetic

### Neon Punch
Black base with clashing neon. For: events, music, gaming, nightlife.
```css
:root {
  --color-bg:      #0d0d0d;
  --color-surface:  #1a1a1a;
  --color-text:     #ffffff;
  --color-muted:    #666666;
  --color-accent:   #ff2d6b;
  --color-accent-2: #00f0ff;
}
```

### Citrus Burst
White base with orange-yellow energy. For: food, fitness, youth-oriented.
```css
:root {
  --color-bg:      #fffbf5;
  --color-surface:  #ffffff;
  --color-text:     #1a1200;
  --color-muted:    #8c7a5a;
  --color-accent:   #ff6d00;
  --color-accent-2: #ffc800;
}
```

### Electric Coral
Dark base with coral-pink warmth. For: social, dating, lifestyle apps.
```css
:root {
  --color-bg:      #12101c;
  --color-surface:  #1e1b2e;
  --color-text:     #f0e6ff;
  --color-muted:    #7b6f99;
  --color-accent:   #ff6b8a;
}
```

---

## Earthy & Natural

### Forest Floor
Deep green base with warm highlights. For: sustainability, outdoor, wellness.
```css
:root {
  --color-bg:      #1a2e1a;
  --color-surface:  #243524;
  --color-text:     #e8ead5;
  --color-muted:    #7a8c6e;
  --color-accent:   #d4a843;
}
```

### Desert Sand
Warm tan with terracotta. For: artisan brands, architecture, crafts.
```css
:root {
  --color-bg:      #f2e8d9;
  --color-surface:  #faf4ea;
  --color-text:     #3d2e1e;
  --color-muted:    #9c8772;
  --color-accent:   #c45a3c;
}
```

### Moss Stone
Cool gray-green, grounded. For: environmental, botanical, science.
```css
:root {
  --color-bg:      #e8ebe4;
  --color-surface:  #f4f6f1;
  --color-text:     #2a3028;
  --color-muted:    #6b7a66;
  --color-accent:   #3d6b4f;
}
```

---

## Pastel & Soft

### Lavender Dream
Soft purple with warm pink accent. For: meditation, beauty, wellness.
```css
:root {
  --color-bg:      #f5f0fa;
  --color-surface:  #fdfbff;
  --color-text:     #2d2640;
  --color-muted:    #9b8fb5;
  --color-accent:   #d97cb5;
}
```

### Cotton Candy
Pink-blue gradient feel. For: children, creative tools, whimsical UIs.
```css
:root {
  --color-bg:      #fef0f5;
  --color-surface:  #ffffff;
  --color-text:     #3a2c3e;
  --color-muted:    #b0a0b8;
  --color-accent:   #6eb5ff;
  --color-accent-2: #ff8ec4;
}
```

---

## Monochrome

### True Mono
Pure grayscale with no color. For: photography, typography-focused, minimalist.
```css
:root {
  --color-bg:      #ffffff;
  --color-surface:  #f5f5f5;
  --color-text:     #111111;
  --color-muted:    #888888;
  --color-accent:   #111111; /* accent IS the text */
}
```

### Inverted Mono
Dark monochrome. For: portfolios, art galleries, cinematic.
```css
:root {
  --color-bg:      #111111;
  --color-surface:  #1c1c1c;
  --color-text:     #eeeeee;
  --color-muted:    #666666;
  --color-accent:   #ffffff;
}
```

---

## Usage Notes

- Pair with font choices from `font-pairings.md` that match the same mood
- `--color-accent` should be used sparingly: CTAs, links, active states, key highlights
- `--color-muted` for secondary text, borders, disabled states, captions
- `--color-surface` for cards, modals, elevated elements over `--color-bg`
- Test contrast ratios: text on bg should meet WCAG AA (4.5:1 for body, 3:1 for large text)
