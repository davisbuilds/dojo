# Canvas (.canvas)

`.canvas` files are [JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/): one object with `nodes` and `edges` arrays. Array order is z-order (first = bottom), so list groups before the nodes they contain. There is no CLI support for canvases; write the JSON directly.

## Format

```json
{
  "nodes": [
    {"id": "a1b2c3d4e5f60718", "type": "group", "x": -40, "y": -60, "width": 920, "height": 380, "label": "Inputs", "color": "4"},
    {"id": "6f0ad84f44ce9c17", "type": "text", "x": 0, "y": 0, "width": 360, "height": 160, "text": "# Goal\n\nShip **v1**"},
    {"id": "0c1d2e3f4a5b6c7d", "type": "file", "x": 460, "y": 0, "width": 380, "height": 280, "file": "Projects/Plan.md", "subpath": "#Scope"},
    {"id": "9e8d7c6b5a4f3e2d", "type": "link", "x": 0, "y": 420, "width": 360, "height": 200, "url": "https://jsoncanvas.org"}
  ],
  "edges": [
    {"id": "f0e1d2c3b4a59687", "fromNode": "6f0ad84f44ce9c17", "fromSide": "right", "toNode": "0c1d2e3f4a5b6c7d", "toSide": "left", "label": "details"}
  ]
}
```

All nodes require `id`, `type`, `x`, `y`, `width`, `height` (integers, pixels; `x`/`y` is the top-left corner, `y` grows downward, negatives allowed). Optional `color`.

| Node type | Required | Optional |
|-----------|----------|----------|
| `text` | `text` (Markdown) | |
| `file` | `file` (vault-relative path, any file type) | `subpath` (`#Heading` or `#^block-id`) |
| `link` | `url` | |
| `group` | | `label`, `background` (image path), `backgroundStyle` (`cover`, `ratio`, `repeat`) |

Edges require `id`, `fromNode`, `toNode`. Optional: `fromSide`/`toSide` (`top`, `right`, `bottom`, `left`), `fromEnd` (default `none`) and `toEnd` (default `arrow`) as `none` or `arrow`, `color`, `label`.

Colors: presets `"1"`–`"6"` (red, orange, yellow, green, cyan, purple — apps choose the exact shade) or hex `"#RRGGBB"`, always as strings.

## Pitfalls

- **Newlines in `text`:** a real JSON escape `\n`, never `\\n`, which renders as literal backslash-n. Writing the file with a JSON serializer rather than string concatenation avoids this.
- **IDs:** any string unique across nodes *and* edges; Obsidian itself generates 16 lowercase hex characters. Every `fromNode`/`toNode` must name an existing node.
- **Group membership is geometric.** There is no parent field; a node belongs to a group when its rectangle lies inside the group's. Size groups to enclose their children with 20–50 px padding.
- **File nodes** use the vault-relative path with extension (`Folder/Note.md`), not a wikilink. Renaming the note outside Obsidian breaks the node.
- **Text nodes don't auto-size**, so content that overflows is clipped; size them to their text (roughly 300–450 px wide for a short paragraph). Readable defaults otherwise: 50–100 px between nodes, coordinates on a 10 or 20 px grid.

## Checks

- The file parses as JSON with only `nodes` and `edges` at the top level.
- IDs are unique across nodes and edges; every edge endpoint exists.
- Each node has its type's required fields; enum values (`type`, sides, ends, `backgroundStyle`) are from the lists above.
- Every `file` node path exists in the vault, and children sit inside their group's bounds.
