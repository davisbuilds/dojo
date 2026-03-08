---
name: obsidian-canvas
description: Create and edit Obsidian Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian.
---

# Obsidian Canvas Skill

Obsidian Canvas uses the [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/) — an open JSON-based format for infinite canvas data. Canvas files use the `.canvas` extension.

## File Structure

```json
{
  "nodes": [],
  "edges": []
}
```

## Nodes

Four node types: `text`, `file`, `link`, `group`. Nodes are z-ordered by array position (first = bottom, last = top).

### Common Attributes (all nodes)

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `id` | Yes | string | Unique 16-char hex identifier |
| `type` | Yes | string | `text`, `file`, `link`, or `group` |
| `x` | Yes | integer | X position in pixels |
| `y` | Yes | integer | Y position in pixels |
| `width` | Yes | integer | Width in pixels |
| `height` | Yes | integer | Height in pixels |
| `color` | No | canvasColor | Preset `"1"`-`"6"` or hex `"#FF0000"` |

### Text Nodes

```json
{
  "id": "6f0ad84f44ce9c17",
  "type": "text",
  "x": 0, "y": 0, "width": 400, "height": 200,
  "text": "# Hello World\n\nThis is **Markdown** content."
}
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `text` | Yes | Plain text with Markdown syntax |

**Newline pitfall:** Use `\n` in JSON strings, not `\\n` — Obsidian renders `\\n` as literal characters.

### File Nodes

```json
{
  "id": "a1b2c3d4e5f67890",
  "type": "file",
  "x": 500, "y": 0, "width": 400, "height": 300,
  "file": "Attachments/diagram.png",
  "subpath": "#Implementation"
}
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `file` | Yes | Path to file within the system |
| `subpath` | No | Link to heading or block (starts with `#`) |

### Link Nodes

```json
{
  "id": "c3d4e5f678901234",
  "type": "link",
  "x": 1000, "y": 0, "width": 400, "height": 200,
  "url": "https://obsidian.md"
}
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | External URL |

### Group Nodes

```json
{
  "id": "d4e5f6789012345a",
  "type": "group",
  "x": -50, "y": -50, "width": 1000, "height": 600,
  "label": "Project Overview",
  "color": "4",
  "background": "Attachments/bg.png",
  "backgroundStyle": "cover"
}
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `label` | No | Text label |
| `background` | No | Path to background image |
| `backgroundStyle` | No | `cover`, `ratio`, or `repeat` |

## Edges

```json
{
  "id": "0123456789abcdef",
  "fromNode": "6f0ad84f44ce9c17",
  "fromSide": "right",
  "fromEnd": "none",
  "toNode": "b2c3d4e5f6789012",
  "toSide": "left",
  "toEnd": "arrow",
  "color": "1",
  "label": "leads to"
}
```

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `id` | Yes | - | Unique identifier |
| `fromNode` | Yes | - | Source node ID |
| `fromSide` | No | - | `top`, `right`, `bottom`, `left` |
| `fromEnd` | No | `none` | `none` or `arrow` |
| `toNode` | Yes | - | Target node ID |
| `toSide` | No | - | `top`, `right`, `bottom`, `left` |
| `toEnd` | No | `arrow` | `none` or `arrow` |
| `color` | No | - | Line color |
| `label` | No | - | Text label |

## Colors

| Preset | Color |
|--------|-------|
| `"1"` | Red |
| `"2"` | Orange |
| `"3"` | Yellow |
| `"4"` | Green |
| `"5"` | Cyan |
| `"6"` | Purple |

Or use hex: `"#FF0000"`. Preset color values are intentionally undefined — apps use their own brand colors.

## ID Generation

16-character lowercase hex string (64-bit random value): `"6f0ad84f44ce9c17"`

## Layout Guidelines

- Coordinates can be negative (canvas extends infinitely)
- `x` increases right, `y` increases downward, position = top-left corner
- Suggested node widths: 200-300 (small), 300-450 (medium), 400-600 (large)
- Leave 20-50px padding inside groups, 50-100px between nodes
- Align to grid (multiples of 10 or 20) for cleaner layouts

## Validation Rules

1. All `id` values must be unique across nodes and edges
2. `fromNode` and `toNode` must reference existing node IDs
3. Required fields must be present for each node type
4. `type` must be one of: `text`, `file`, `link`, `group`
5. `backgroundStyle` must be one of: `cover`, `ratio`, `repeat`
6. `fromSide`, `toSide` must be one of: `top`, `right`, `bottom`, `left`
7. `fromEnd`, `toEnd` must be one of: `none`, `arrow`
8. Color presets must be `"1"` through `"6"` or valid hex color

For complete worked examples (mind map, project board, research canvas, flowchart), see `references/examples.md`.

## When To Use

- When creating or editing `.canvas` files for Obsidian or compatible apps
- When building visual canvases, mind maps, flowcharts, or project boards
- When the user mentions Canvas files, infinite canvas, or Obsidian canvas

## Boundaries

- Not for general JSON editing unrelated to the JSON Canvas spec
- Not for Mermaid, PlantUML, or other diagram-as-code formats
- Not for Obsidian plugin development or vault configuration
- Skip when the user needs interactive canvas editing — this skill produces static `.canvas` files

## Output

- Valid `.canvas` files conforming to JSON Canvas Spec 1.0
- Nodes with unique 16-character hex IDs positioned on a coordinate grid
- Edges referencing valid node IDs with optional labels, colors, and side/end attributes

## References

- [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/)
- [JSON Canvas GitHub](https://github.com/obsidianmd/jsoncanvas)
