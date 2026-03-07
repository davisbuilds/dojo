---
name: theme-factory
description: Toolkit for styling artifacts with a theme. Use when users ask to theme slides, docs, reports, or HTML pages using curated font/color systems or a generated custom theme.
license: Complete terms in LICENSE.txt
---


# Theme Factory Skill

This skill provides a curated collection of professional font and color themes themes, each with carefully selected color palettes and font pairings. Once a theme is chosen, it can be applied to any artifact.

## Purpose

To apply consistent, professional styling to presentation slide decks, use this skill. Each theme includes:
- A cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- A distinct visual identity suitable for different contexts and audiences

## Usage Instructions

To apply styling to a slide deck or other artifact:

1. **Show the theme showcase**: Display the `theme-showcase.pdf` file to allow users to see all available themes visually. Do not make any modifications to it; simply show the file for viewing.
2. **Ask for their choice**: Ask which theme to apply to the deck
3. **Wait for selection**: Get explicit confirmation about the chosen theme
4. **Apply the theme**: Once a theme has been chosen, apply the selected theme's colors and fonts to the deck/artifact

## Themes Available

The following 10 themes are available, each showcased in `theme-showcase.pdf`:

1. **Ocean Depths** - Professional and calming maritime theme
2. **Sunset Boulevard** - Warm and vibrant sunset colors
3. **Forest Canopy** - Natural and grounded earth tones
4. **Modern Minimalist** - Clean and contemporary grayscale
5. **Golden Hour** - Rich and warm autumnal palette
6. **Arctic Frost** - Cool and crisp winter-inspired theme
7. **Desert Rose** - Soft and sophisticated dusty tones
8. **Tech Innovation** - Bold and modern tech aesthetic
9. **Botanical Garden** - Fresh and organic garden colors
10. **Midnight Galaxy** - Dramatic and cosmic deep tones

## Theme Details

Each theme is defined in the `themes/` directory with complete specifications including:
- Cohesive color palette with hex codes
- Complementary font pairings for headers and body text
- Distinct visual identity suitable for different contexts and audiences

## Application Process

After a preferred theme is selected:
1. Read the corresponding theme file from the `themes/` directory
2. Apply the specified colors and fonts consistently throughout the deck
3. Ensure proper contrast and readability
4. Maintain the theme's visual identity across all slides

## Create your Own Theme
To handle cases where none of the existing themes work for an artifact, create a custom theme. Based on provided inputs, generate a new theme similar to the ones above. Give the theme a similar name describing what the font/color combinations represent. Use any basic description provided to choose appropriate colors/fonts. After generating the theme, show it for review and verification. Following that, apply the theme as described above.

## When To Use

- User asks to theme, style, or brand a slide deck, document, report, or HTML page
- User wants to choose from curated font/color systems for an artifact
- User needs a custom theme generated from a description or brand guidelines
- Applying consistent colors, fonts, and visual identity across multiple slides or pages

## Boundaries

- Not for building frontend components or full web applications (use frontend-design instead)
- Not for editing slide content, structure, or narrative; only visual styling
- Skip when the user needs accessibility audits or UX reviews rather than theming
- Do not modify `theme-showcase.pdf`; it is read-only for user preview

## Output

- The target artifact restyled with the selected or generated theme's colors and fonts
- Consistent application of the theme across all slides/pages in the artifact
- Proper contrast and readability maintained throughout

## Verification

- All slides/pages use only colors and fonts from the selected theme
- Text maintains readable contrast ratios against its background
- Font pairings are applied correctly (display font for headers, body font for text)
- The theme's visual identity is cohesive across the entire artifact

## Resources

- `themes/` -- 10 curated theme definitions (`.json` + `.md` per theme)
- `assets/theme-template.html` -- HTML template for theme preview
- `scripts/generate_css.py` -- generates CSS from a theme definition
- `scripts/preview_theme.py` -- renders a visual preview of a theme
