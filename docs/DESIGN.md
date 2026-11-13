# Design rules

The site should read as a calm reading library: few choices per screen, type doing the work, and portraits of the saints and authors as the visual interest. These rules apply to every page and to both themes. When a rule here and the existing code disagree, follow the code and record the mismatch (AGENTS.md rule 11). The owner approved this pass on November 12, 2026.

## Type

- **Serif for reading.** Everything a reader reads (titles, headings, descriptions, notes, rows, the hosted texts) is set in the existing serifs: `--display` (Cormorant Garamond) for headings and `--serif` (EB Garamond) for text. Sans-serif (`--sans`) is only for small controls: buttons, form fields, the toolbar, and the navigation.
- **Measure.** Running text sits at 60 to 70 characters a line (`max-width: 66ch` on prose, about 34em for the reader).
- **Labels** are small caps (`font-variant-caps: all-small-caps; letter-spacing: .06em`), not tracked uppercase sans.
- **Numerals** in running text are old-style (`font-variant-numeric: oldstyle-nums`); tables and counters may use lining figures.
- **One type scale:** 14, 16, 18, 21, 26, 34, 48 px (`--t-xs` to `--t-3xl`). **One spacing scale:** 4, 8, 12, 16, 24, 32, 48, 64 px (`--s-1` to `--s-8`). No other sizes in new rules.
- No new fonts.

## Controls

Exactly three styles:

1. **Filled primary** (`.btn`): rubric fill. **At most one per screen.** It is the single thing the page wants you to do (for example "Read here", "Enter the reading room").
2. **Outlined secondary** (`.btn.ghost`): a hairline rubric border, no fill.
3. **Text link**: underlined serif or small sans, rubric. Use this for everything else, including rows of actions.

Gold buttons (`.btn.gold`) and pill buttons are retired. Buttons have 6 px corners, not pills. Icon buttons (theme, menu) keep their square shape.

## Containers

- A container has **a border or a tint, never both**, and no shadow.
- **No bordered card inside a bordered panel.**
- Prefer **rows separated by hairline dividers** to grids of cards. A list of works, editions, or links is a list of rows.

## Notices

- Each notice appears **once** on a page, at the **smallest legible size** (14 px), **nearest the thing it concerns**.
- Longer evidence (rights notes, checked dates, method, licence text) sits behind a `<details>` disclosure on the same page, or at the end of the text in the reader. It is never removed from the page source.
- Caveats that apply to the whole site ("listing is not endorsement", "files are served by the original library", "dates are distinct") live once on the policy or about page, not on primary surfaces.
- Required notices (the FTC affiliate line beside affiliate links, Project Gutenberg notices, Wikipedia and portrait credits, rights badges, editorial context notes on flagged titles) are never removed; they are made small and placed beside what they concern.

## Accessibility

Visible focus on every control, keyboard access, and contrast of at least 4.5:1 for text in both themes. Fixed image dimensions so nothing jumps while loading.
