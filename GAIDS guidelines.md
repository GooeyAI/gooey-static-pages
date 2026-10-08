# GAIDS design guidelines

How to design with GAIDS, the Gooey design system: what to do, why, and which token or component to use. Written for the designer who owns GAIDS, for agents that build screens in Figma from the library, and for front-end developers.

**Status:** first full draft, 2026-10-06, reviewed once on 2026-10-07 (live Figma fact-check, source attribution, coherence, coverage). Values were measured from the live GAIDS Figma file (`7wRztN1MVtGDdox6PfctVs`) and the code on those dates. Figma is the source of truth for colour, spacing and radius: if a number here disagrees with the file, the file wins, so re-measure and fix this document. Distilled from `PRODUCT.md`, the standing rules in `DESIGN_TOKENS.md` and `GAIDS_CHANGELOG.md`, `Astryx guideline.md` and nine reference digests in `design-systems/` (Appendix D).

## How to read this

- **Precedence.** `PRODUCT.md` for principles and anti-references; the live GAIDS Figma file for colour, spacing and radius values; decisions already written in `DESIGN_TOKENS.md` and the changelog; then this document; then the reference systems. Where `DESIGN_TOKENS.md` quotes a value that disagrees with Figma (its migration table does), Figma wins. Where a reference disagrees with GAIDS, GAIDS wins (Appendix D lists the differences).
- **Each rule** is a bold instruction, a sentence of why, then *GAIDS:* how it applies here (exact token, style or component names) and *Refs:* where the support comes from. Rule ids (C6, A4) are for citing in reviews.
- **Tags.** **[gap]** GAIDS Figma or code deviates from the rule today, with the measured value. **[open]** the owner has not decided. **[proposal]** a new rule, token or component that needs the owner's sign-off; do not treat it as shipped. **[2.2]** a WCAG 2.2 addition worth adopting early. A tag in the bold heading marks the whole rule; a tag inside the GAIDS line marks one clause. Quoted strings are examples from Playground drafts and need sign-off; only the Report copy is approved.
- **Code is not migrated yet.** Rules describe Figma's target state; code still ships old token names, no dark block and different radius steps (Appendix B #16). Never describe code as already matching Figma.
- **Appendices** hold the contrast tables (A), known gaps (B), decisions for the owner (C), the reference map (D) and topics not yet covered (E).

## The twelve rules that carry most weight

1. **Quiet by default.** Everything neutral; colour and weight only for selection, the primary action, real status and the eco figures (P3, C2).
2. **Bind everything.** No hex, no typed pixel value, no typed shadow. Colour, space, radius, text and effects come from variables and styles; zero is `space/0` (P7, L1, L2).
3. **Surfaces have jobs.** `bg/page` holds content, `bg/surface` is the ground, `bg/panel` is an inset. Climb the separation ladder (space, hairline, tone, border, shadow) only as far as needed (N1, N2).
4. **No cards in cards; records are rows.** Compare-and-act lists are hairline rows, not one card each (N3, N4).
5. **One primary `Button` per container**, and the primary is ink, not a brand colour (N6, C3).
6. **Rank by weight and ink at one size.** Aim for three sizes per panel, 16, 14 and 12, plus 18 for a stat value (T3; T5 is a proposal).
7. **Status is words plus a marker, never colour alone.** Red failed, amber blocked but recoverable, teal running; no green (C6, C7, C8).
8. **Numbers lead.** Exact, unit beside, right-aligned, same format down a column, estimates labelled as estimates (P2, T10, W8).
9. **Design both modes and every state.** 4.5:1 text, 3:1 non-text, a visible focus ring, keyboard order, Light, Dark and phone (A1 to A7, B13).
10. **Plain words.** Sentence case, verb-first buttons, errors that say what happened and what to do next (W2 to W4, W10).
11. **AI that stays in the person's hands.** Cost and CO₂e together, confirm anything with real-world effect, a way to stop, no sparkles or glow (AI2, AI5, AI7, AI9).
12. **Build from the library.** Figma is the source of truth; screens use library instances and slots; unapproved ideas are drawn as proposals, not components (B8, B9, B14).

---

## 1. Principles

P1 to P5 are the product principles from `PRODUCT.md`. P6 to P8 are proposed additions that each already have standing rules behind them. Run each *Test* on every screen. Examples marked (proposal) are unapproved Playground frames.

**P1. Earned familiarity: use standard patterns (search, filters, list plus detail, segmented control) so the tool disappears into the task.** *Test:* would a first-time builder recognise this control from another product? *GAIDS:* every menu is an `Overlay/Menu Shell`; `Tab` has three fixed jobs; the model picker (proposal) is search, filters, list plus detail and a segmented control. *Refs:* PRODUCT.md; Apple, Fluent, Carbon.

**P2. Precision you can scan: lead with the number, and compare like with like in the same position and format.** *Test:* can two rows be compared by reading down one column? *GAIDS:* a stat card stacks a `Meta` label, a `Heading/H3` value and a `Body/Small` caption; the top bar puts "$0.10" over "1.1 g CO₂e". The picker's four chips sit in fixed slots as data cells, not decoration: PRODUCT.md's chip and hero-tile anti-references bite when a chip repeats what the row already shows, or a tile shows one number with no comparison. *Refs:* Polaris, Primer, Spectrum, Stripe.

**P3. Quiet by default: keep everything neutral, and reserve colour and weight for selection, the primary action, real status and the eco figures.** *Test:* what does each coloured, bold or boxed element mark? If none of those, neutralise it. *GAIDS:* the primary `Button` is ink on paper; `Switch` On is ink, never teal; a collapsed `Chat/Activity` is one muted line. *Refs:* Apple, Polaris, Spectrum.

**P4. Decide in one pass: show enough in the list and detail to choose, and reveal the rest progressively.** *Test:* can the person finish this decision here, and is anything shown that the decision does not need? *GAIDS:* the picker (proposal) pairs a list, a detail pane and a footer naming the chosen model and region; `Chat/Error Bubble` keeps raw error text behind "Technical details". *Refs:* Material, Fluent, Polaris.

**P5. Plain words: say what a metric means, and never leave an abbreviation unexplained.** *Test:* would someone outside the field know every label and unit here without hovering? *GAIDS:* error copy says whose problem it is ("a setup issue, not something you did"). **[open]** picker chips use "ZDR", "g/M" and "/1M"; the one-line legend that explains them is proposed (AI5), not drawn. *Refs:* Carbon, Polaris, Atlassian.

**P6. [proposal] Honest about AI, cost and uncertainty: show the figure, say how it was estimated, and label invented sample data.** *Test:* does every cost, footprint or AI action say what it is and how sure we are? *GAIDS:* the top-bar readout opens the Eco modal, which flags "Low confidence"; `Chat/Activity` reads "Thought for 2s, 3 tools used". *Refs:* Apple (confidence as concepts, not scores), Fluent (be specific about data and limits), Carbon (explainability on request), Atlassian ("pop the hood"), Stripe (demo banner for sample data).

**P7. [proposal] Tokens, not literals: bind every colour, space, radius, text style and effect to a GAIDS variable or style.** *Test:* does Inspect show a variable or a named style, and no literal, on every fill, stroke, space, radius, text and effect? *GAIDS:* about 97% of paddings and gaps are bound in 8 of 9 audited frames. Literals allowed: third-party brand marks, flag artwork, documentation chrome; if no token fits, leave the value literal and list it. **[gap]** the Eco frames are about half literal; Home headings are unstyled Inter. *Refs:* Material, Carbon, Atlassian, Polaris.

**P8. [proposal] Accessible by default: design contrast and non-colour cues in, instead of auditing them later.** *Test:* does any state rely on colour alone, and does every text pair reach 4.5:1 on its real surface? *GAIDS:* `bg/selected` always pairs with a second cue; run-chip borders are decorative because text carries the state. *Refs:* Carbon, Fluent, Material, Atlassian.

---

## 2. Composition and hierarchy

Builds on `Astryx guideline.md`, tested against GAIDS screens. Astryx's own numbers (type base 14 ratio 1.2, 1024/768 region thresholds, none/low/med/high elevation, "two text colours only") are not GAIDS rules.

**N1. Pick surfaces by role: `bg/page` holds content, `bg/surface` is the ground behind it, `bg/panel` is an inset, `bg/selected` and `bg/hover` mark state.** One role per job keeps layers legible in both modes; a role nested in itself disappears. *GAIDS:* `bg/page` is the canvas of every pane, card, dialog, menu and the top bar; `bg/surface` is `Nav/Sidebar Rail` and the dialog body behind `bg/page` cards; `bg/panel` is chips, tab tracks, the picker search field, user bubbles and glyph tiles. **[gap]** roles are read from screens: 35 of 43 token descriptions are empty, and two of the few that exist are stale (`bg/selected` ratios, `run/running-ink`). *Refs:* Apple, Carbon, Material, Stripe.

**N2. Climb the separation ladder one rung at a time and stop where it reads: space, hairline, tonal fill, border, shadow.** Heavier rungs add noise to dense screens. *GAIDS:* space first; then `line/soft`; then `bg/panel`; then a 1px `line/soft` container; then an `Elevation/*` style, only on parts that cover content. Screens carry roughly 20 to 40 `line/soft` strokes against 1 to 4 effects. **[gap]** `Workspace/Pane`, `Shell/App Shell` and `RunStatus/Chip` carry shadows without covering anything (Appendix B #12). *Refs:* Atlassian, Carbon, Material, Primer.

**N3. Never put a bordered card inside a bordered card.** Nested boxes stack borders and radii and bury content. *GAIDS:* standing rule from the Choose-a-model rebuild. **[open]** whether `Workspace/Pane` is a frame or a card (Appendix C #8): it draws like a card (1px `line/soft`, `radius/big`) yet holds `Settings/Section` cards, so until decided one card level inside a pane is allowed. *Refs:* Astryx; Polaris allows one inset level.

**N4. Draw records you compare or act on as rows between hairlines; use cards only for browse galleries and settings groups.** A card per record repeats borders and hides alignment. *GAIDS:* Tools and Knowledge lists are hairline rows, each led by a 32px `bg/panel` glyph tile; `Card/Industry Tile` and `Card/News` are browse galleries and fit. **[gap]** Home draws Recent and Saved workflows as 4-up card grids (`Workflow/Card History`, `Workflow/Card Saved`), close to PRODUCT's "identical card grids" anti-reference. **[open]** whether per-industry tile hover colour (`Tag.color`) becomes a token. *Refs:* Astryx, Polaris, Spectrum.

**N5. Let the container own padding and gap, and set every label in a region on one content line.** Child margins make edges drift; a component with its own inset takes less container padding. *GAIDS:* `Overlay/Menu Shell` padding `space/1` plus the 12px `Overlay/Menu Item` inset puts text 16px in, as do `Nav/Sidebar Rail` rows (8) plus `Nav/Item` (8); `Modal/Dialog` is an empty slot, so its content owns the padding. Use auto layout and slots, never hand-placed frames. *Refs:* Carbon, Atlassian, Polaris, Astryx.

**N6. Give each region one lead and each container one primary `Button`.** Two leads compete and scanning stalls. *GAIDS:* one `Button kind=primary` per container: Run in `Topbar/Bar`; Use model, Done or Send report in a dialog footer beside a secondary Cancel. Two primaries share a screen only across separate panes. *Refs:* Astryx, Stripe, Carbon, Fluent, Material (one primary); Apple allows one or two prominent buttons.

**N7. Frame first: start every screen from `Shell/App Shell` (or `Mobile/Screen`), and let the frame own headers, footers and rails.** Hand-built chrome drifts and scrolls away with the body. *GAIDS:* `Shell/App Shell` nests `Nav/Sidebar Rail`, `Topbar/Bar` and `Workspace/Pane`, whose `content` slot takes a `Workspace/<Tab> Panel`. **[gap]** `Modal/Dialog` has only a `content` slot, so Integrations, Eco, the picker and Report each redraw the 52px header and hairline footer. *Refs:* Material, Carbon, Atlassian.

---

## 3. Colour

Ratios are Light / Dark from the live WCAG 2.1 audit. The pairing tables and every failing pair are in Appendix A.

**C1. Bind every fill, stroke, text colour and effect colour to a `Color/Semantic` variable, chosen by its role, never a primitive, a hex value or an `rgb()` literal.** Roles survive a mode switch; literals do not, and two tokens can match in Light yet split in Dark (`icon/muted` is lighter than `icon/tertiary` in Light, darker in Dark). *GAIDS:* `.Color/Primitives` is hidden with empty scopes; text takes `text/*`, icons take `icon/*`; an icon on a coloured fill or carrying status keeps `action/on-primary`, `text/inverse` or `status/*`. **[gap]** library literals: Button `icon-primary` hover and disabled; Composer WhatsApp send `#21d562`; `#ffffff` fills on five slot nodes (white boxes in Dark); `Brand/Builder Logo` binds a primitive. *Refs:* Material, Primer, Polaris, Carbon.

**C2. Build screens from neutrals; spend colour only on selection, the one primary action, real status and the eco figures.** Colour that appears everywhere stops carrying meaning. *GAIDS:* grounds `bg/page`, `bg/surface`, `bg/panel`; ink `text/*`, `icon/*`; edges `line/*`. Cards and rows carry no tint; no glows, glass or gradients. Charts follow the same budget: lead with ink, push context back with neutrals, label series directly, never use status colours as series; no chart tokens exist and chart colours stay literal **[open]** until the first real chart. *Refs:* Carbon, Fluent, Polaris, Atlassian.

**C3. Make the primary action ink: an `action/primary` fill with an `action/on-primary` label, never a teal or blue button.** Emphasis then comes from weight and position, leaving colour for status. *GAIDS:* near-black in Light, near-white in Dark (18.80 / 16.70 on `bg/page`). **[gap]** `bg/primary-hover` (white 10%) is invisible on the Dark primary Button. *Refs:* Polaris, Spectrum, Astryx.

**C4. Keep brand teal and blue to their jobs: teal for running, success and eco; blue for upload progress.** Large brand areas flatten hierarchy. *GAIDS:* `brand/gooey-teal` equals `status/success`; `brand/gooey-blue` draws the 2px upload line, which is none of selection, action, status or eco **[open]**. *Refs:* Fluent, Apple, Polaris.

**C5. Keep third-party brand colours literal and separate. Never map them onto semantic tokens, and do not "fix" their contrast.** The partner owns the pairing. *GAIDS:* `.Color/WhatsApp` (hidden, hex only); Twilio is neutral. **[gap]** white on `whatsapp/brand` is 1.98 in both modes; code returns `#21d562`, not `#25d366`. *Refs:* standing rule.

**C6. Give each status colour one meaning: coral for a failed run, amber for blocked but recoverable, teal for running.** A colour with two meanings gets ignored. *GAIDS:* `status/danger` with `run/error-*`; `status/warning` with `run/warn-*` (insufficient funds, Cancelled); `run/running-*`. `status/success` is the same teal where an eco figure or confirmation needs it, but a Completed or Success run chip is neutral (C8). There is no `status/info`: information is neutral (`bg/panel`, `line/soft`, circle-info icon). *Refs:* Apple, Polaris, Spectrum, Carbon.

**C7. Never rely on colour alone: pair every status colour with a marker or icon and a text label.** People read colour differently (vision, screens, culture). *GAIDS:* `RunStatus/Chip` has a dot or icon plus a label; `Chat/Error Bubble` an icon plus a title. Chip borders (`run/*-line`) are decorative and exempt from 3:1. **[gap]** `Mobile/Topbar` `showDot` is a bare dot. *Refs:* Apple, Carbon, Primer, Spectrum.

**C8. Do not add green: success is teal, and a Completed chip stays neutral.** One hue family keeps status calm. *GAIDS:* `status/success` is `teal/800` Light, `teal/400` Dark; Completed is `bg/page`, `line/soft`, `text/primary`. *Refs:* standing decision; most references use green and GAIDS departs from them (Appendix D).

**C9. Tint with opaque tokens, never alpha: wash from `run/*-bg`, a 1px `run/*-line`, sentence text in `text/primary`.** Figma drops opacity on variable-bound paints, and status ink on a wash is thin or failing. *GAIDS:* status ink only on the icon and a short label. Alphas allowed: `bg/scrim`, `bg/primary-hover`, `bg/active`, the Slider halo, black shadows. Warning notice: `run/warn-bg` plus `run/warn-line`; info notice: `bg/panel` plus `line/soft`, never `bg/info`. *Refs:* Spectrum, Atlassian, Primer.

**C10. Mark selection with `bg/selected` plus a second cue (bold label, ink edge or check). Never tint it with an accent.** In Light, selected is only 1.18:1 from `bg/surface`. *GAIDS:* `Nav/Item` active is `bg/selected` plus SemiBold; middle `Tab` active is `bg/panel` plus `line/strong` and an 8px ink dot. **[gap]** `bg/selected` fails `text/tertiary` in both modes (3.73 / 2.58) and `text/secondary` in Dark (3.64): use `text/primary`; low `Tab` active is `bg/selected` with only a colour change (tertiary to primary). *Refs:* Atlassian, Spectrum, Carbon.

**C11. Use one hover fill per component family, one step from rest.** Hover says "this will act" and nothing more. *GAIDS:* `bg/hover` on ghost Buttons and rows; `bg/panel` on `Nav/Item`, `Overlay/Menu Item` and chips. **[open]** two hover fills coexist. **[gap]** Dark `bg/hover` is `surface/600`, lighter than `bg/selected`, and fails every ink token. **[proposal]** repoint it to `surface/800` (Dark `bg/panel`). *Refs:* Carbon, Fluent, Atlassian.

**C12. Treat Dark as its own warm palette, not an inversion: no cool or navy greys in surfaces.** Warm paper in Light needs warm brown in Dark. *GAIDS:* both modes alias the one `surface/` ramp (hue about 30 to 33 degrees); the cool `neutral/` ramp is ink and lines only. *Refs:* Apple, Atlassian, Material, Fluent.

**C13. Keep layer order fixed (`bg/page`, `bg/surface`, `bg/panel`); higher layers go lighter in Dark.** Dark depth comes from tone, not shadow (Dark shadows are S6). *GAIDS:* the order is the same in both modes. *Refs:* Carbon, Spectrum, Material.

**C14. Before adding a token, list the nearest existing token and its measured difference, and add one only if it is clearly different (about 5%).** Near-duplicates drift apart. *GAIDS:* the 13 duplicate `--gooey-status-*` code tokens are the warning. **[open]** the metric behind "about 5%" (lightness or CIELAB distance). *Refs:* Atlassian, Spectrum, Material.

**C15. Name a new token for its role, give it Light and Dark values, scope it narrowly, and state its measured ratio.** Pickers then offer only the right tokens. *GAIDS:* **[gap]** nine tokens use all scopes (`bg/hover`, `bg/active`, `bg/input`, `bg/primary-hover`, `action/secondary`, `switch/on-bg`, `switch/off-bg`, `switch/disabled-bg`, `switch/knob-disabled`). Regenerate descriptions from live values, never retype them. *Refs:* Primer, Atlassian, Carbon, Material.

**C16. Pick a ramp step by measuring contrast on the real background, not by eye.** Closest-looking is often too light. *GAIDS:* running ink is `teal/800` (6.48 on its chip), not the closer `teal/700`; if two roles land on one step, say so (`text/tertiary` absorbed `text/meta`). *Refs:* Stripe, Spectrum, Primer, Carbon.

---

## 4. Typography

GAIDS has 14 local text styles, none bound to variables. These values come from the live styles, not the Foundations captions (the captions for H1, H2, H3 and Code are stale).

| Style | Font, weight | Size / line height | Use it for |
|---|---|---|---|
| `Display` | Domine Regular, tracking -2% | 48 / 120% | Large data numerals only |
| `Heading/H1` | Inter Medium | 40 / 120% | Page title (screens only) |
| `Heading/H2` | Inter Medium | 32 / 120% | Page section title (screens only) |
| `Heading/H3` | Inter Medium | 18 / 120% | Stat value, model name in a detail pane |
| `Heading/H4` | Inter Semi Bold | 16 / 120% | Panel, dialog and card titles |
| `Heading/H5` | Inter Medium | 14 / 120% | Group heading (looks like `UI/Regular`) |
| `Body/Large` | Inter Regular | 16 / 150% | Field values, long reading text |
| `Body/Body` | Inter Regular | 14 / 150% | Running copy in panels, dialogs, cards |
| `Body/Small` | Inter Regular | 12 / 150% | One-line descriptions, helper text, counts |
| `UI/Large` | Inter Medium | 16 / 120% | Card titles and field labels at 16 |
| `UI/Regular` | Inter Medium (not Regular) | 14 / 120% | Labels, menu items, control text |
| `UI/Strong` | Inter Semi Bold | 14 / 120% | Button labels, selected nav items, names |
| `Meta` | Inter Medium | 12 / 120% | Dates, counts, units, chip and tag text |
| `Code` | Menlo Regular | 14 / 150% | Code, JSON, IDs (see T11) |

**T1. Bind every text node to a library text style; when none fits, draw at the nearest style.** One bound style lets a later change reach every screen. *GAIDS:* standing rule; 13 became `Body/Body`, 11 mono became `Code`. **[gap]** about 90% of text inside library components is bound (991 of 1,105); literals remain in the secondary Button label, Avatar initials, Home and shell titles, 56 mono nodes in the library and about 1,350 in Playground. No style binds the Font variables, so a family change will not propagate. *Refs:* Carbon, Spectrum, Primer, Astryx.

**T2. Pick the style from the job the text does, not the size you want.** Role-based choice keeps screens consistent. *GAIDS:* follow the table. `Heading/H5` and `UI/Regular` look identical today; use H5 for a heading and `UI/Regular` for a label so intent survives a later change. *Refs:* Carbon, Material, Atlassian.

**T3. Rank by weight and neutral ink at one size; change size only to open a heading or show a stat value.** Body, label and emphasis share 14, so the eye follows weight and ink, and hue stays for selection and status. *GAIDS:* `Body/Body` Regular, `UI/Regular` Medium, `UI/Strong` Semi Bold over `text/primary`, `text/secondary`, `text/tertiary`; use only Regular, Medium and Semi Bold. **[open]** heading weight: H1 to H3 are Medium, H4 is Semi Bold, production headings render Regular. *Refs:* Astryx (weight and colour, not size). Apple, Atlassian, Polaris, Spectrum and Primer rank by weight, size and colour, so GAIDS departs from them (Appendix D).

**T4. Use `text/primary` for lead text, `text/secondary` for support, and `text/tertiary` only for meta on `bg/page` or `bg/input`.** Tertiary fails 4.5:1 on other grounds (Appendix A). *GAIDS:* no `text/disabled` token exists. *Refs:* Astryx (primary for lead, secondary for support); the third tier is GAIDS's own.

**T5. [proposal] Keep a panel, dialog or card to three sizes: 16 title, 14 body, 12 meta, plus 18 for a stat value.** Fewer registers read as one calm surface. *GAIDS:* a measured convention not yet written down. `Heading/H3` (18) is used for stat values and detail-pane names, and for a few panel titles (`Workspace/Ask Gooey Panel`, Choose a model, Add integrations) where the table says H4 **[open]**. *Refs:* none; Astryx caps hierarchy at about four registers.

**T6. Never set text below 12.** Smaller text is hard to read and has no style. *GAIDS:* `Body/Small` and `Meta` are the floor. **[gap]** Avatar initials are a literal 10. *Refs:* Atlassian, Polaris.

**T7. Keep `Display`, `Heading/H1` and `Heading/H2` out of components; use `Display` only for large data numerals.** They are page-level registers. *GAIDS:* no library component uses them. `Display` appears today only on the Foundations specimen and the Cover; the 2026-10-05 decision was to keep it for the Choose a model key numerals, but the live frames set those in `Heading/H3` **[open]**: restore `Display` there or retire the decision. **[gap]** Home titles are unstyled literals. *Refs:* Astryx, Material, Carbon, Atlassian.

**T8. Cap running text at about 80 characters a line, left-align it, and never justify it.** Long lines and uneven spacing slow reading. *GAIDS:* `Modal/Dialog` (520) and the minor `Workspace/Pane` (400) hold the measure; in a solo pane (1000) use a narrower column. Centre only splash and empty-state copy. *Refs:* Atlassian, Primer, Spectrum, Fluent.

**T9. Wrap before truncating. Truncate only names, IDs and URLs; keep titles, labels, buttons, errors and numbers whole; reveal cut text in a tooltip.** Cut text hides meaning. *GAIDS:* `Overlay/Tooltip` for cut names, a middle ellipsis for IDs and file names. Model Row chip slots are fixed (56, 124, 76), so labels must fit. *Refs:* Carbon, Material, Fluent, Spectrum.

**T10. Lead with the number, label it, put the unit beside it, and right-align numbers and dates at the row end; compare like with like.** Numbers are what builders compare, and mismatched units turn comparison into arithmetic. *GAIDS:* `Heading/H3` value over a `Body/Small` `text/tertiary` caption; `Topbar/Eco Readout` right-aligns "$0.10" over "1.1 g CO₂e"; the four model lenses sit in one order across rows, tiles and the compare table. **[open]** how missing eco data shows. **[proposal]** turn on tabular figures for number-bearing styles if a Figma style can store it; never fake alignment with mono. *Refs:* Polaris, Material, Spectrum, Primer.

**T11. Give each face one job: Inter for UI text, Domine for `Display`, one mono face for code, IDs and JSON.** Mixed faces blur hierarchy. *GAIDS:* **[gap]** `Code` points at Menlo, which is macOS-only and cannot load in the Figma plugin, so Playground draws literal Geist Mono; production `--gooey-font-mono` is a system stack. **[open]** which mono face. *Refs:* Apple, Polaris, Atlassian, Stripe.

**T12. Test every text component with Hindi text and with strings 50% longer than English.** Builders write agents for many languages, and short labels can more than double. *GAIDS:* **[open]** Inter and Domine have no Devanagari; production falls back to generic sans-serif. The 120% line height on `UI/*`, `Meta` and `Heading/*` is tight for Devanagari (Material sizes Hindi about 7% taller). Give multi-line text no fixed height. *Refs:* Material, Polaris, Spectrum, Carbon.

---

## 5. Space, layout and responsive behaviour

Measured 2026-10-06. Concentric corners and borders are in section 6; hit areas are in section 9.

**L1. Bind every padding and gap to a `space/*` variable. Never type a number that a step already covers.** One scale keeps rhythm predictable and lets a retune reach every screen. *GAIDS:* `space/0` 0, `/1` 4, `/2` 8, `/3` 12, `/4` 16, `/5` 20, `/6` 24, plus the restricted `space/half` 2. **[gap]** code binds about a quarter of spacing values (135 of 537); Eco frames are about half literal; gap 4 is typed on `About/Card`, `Workspace/About Panel` and `Mobile/About Panel`; unbound zeros remain in Organisms (247) and Molecules (110). *Refs:* Astryx, Polaris, Atlassian, Carbon.

**L2. Bind every zero padding and gap in a component or instance to `space/0`; snap near-misses to the nearest step; keep the deliberate literals and list them.** A bound zero survives a retune and makes a sweep checkable. *GAIDS:* snap within 1px of a step above 0; 9 to 10 becomes `space/3`; values above 24 and the 40px variant-grid frames stay literal; 1px stays literal and is never snapped to `space/0` (it would delete the Switch ring). Skipped on purpose: gaps on space-between frames (the field reads Auto) and plain non-component frames; ask before sweeping those. CSS keeps a bare `0`. **[open]** the remaining 6px and 10px cases (`Workspace/Ask Gooey Panel` gap 6 and padding-right 10, `Mobile/Status Bar` and `Mobile/Screen` gap 6): pick no direction for the owner. *Refs:* Carbon, Astryx, standing rule.

**L3. Use `space/half` and `radius/compact` as a pair, on components about 20px tall or less.** At 2px a step stops reading as layout; the pair keeps a 4px child concentric in a 6px parent. *GAIDS:* Switch Small track 6, inset 2, knob 4. **[gap]** `Chat/Balance Strip` uses `space/half` as a 2px gap on its own, on a 50px strip. **[open]** code names for both (suggested `--gooey-radius-compact`, `--gooey-space-half`). *Refs:* Fluent, Spectrum.

**L4. Space tightly inside a group and generously between groups: gaps inside a group are at most half the gaps between groups.** Proximity is the cheapest grouping signal, and one gap repeated everywhere flattens structure. *GAIDS:* 4 to 8 inside (`space/1`, `/2`), 16 to 24 between (`space/4` to `/6`). Drawn habit: 4 for label-control-help stacks, 8 between siblings, 12 for rows, 16 for pane and card bodies, 24 at dialog and settings edges. *Refs:* Astryx, Polaris, Carbon, Fluent.

**L5. Build the workspace from inset `Workspace/Pane` panes 12px apart: two side by side (major plus minor, or one solo); a third pane or side panel needs the owner's sign-off.** More panes starve each other. *GAIDS:* a pane is `bg/page`, 1px `line/soft`, `radius/big`; roles are major (600), minor (400) and solo (1000), about 60/40 in code. `Nav/Sidebar Rail` (264 expanded, 52 collapsed) keeps only a right-edge line (`line/default` expanded, the `Right border subtle` effect collapsed) with no radius or shadow; the Ask Gooey side panel has no border at all. **[gap]** the rail description and code say collapsed is 64; the panel is drawn 440 while code and the unbound `sidebar/open-width` variable say 460. *Refs:* none; drawn GAIDS layout (Material limits a window to three panes).

**L6. Switch the workspace layout once, at 992px: below it every split is one pane, and phones and tablets share that layout.** Production has one switch for the workspace and top bar and no tablet layout. *GAIDS:* Bootstrap `lg` (`max-width: 991.98px` / `min-width: 992px`, JS `LG_BREAKPOINT_PX`); desktop frames are 1417 to 1440 wide, phones 390 x 844. Exceptions in code: the Ask Gooey side panel goes full screen below 1140 (460 open above) and Home grids change at 768 and 992 **[open]** which of these the phone frames should follow. **[open]** tablets from 769 to 991 get the phone layout. *Refs:* none; production fact. Astryx (1024 / 768), Material, Primer and Polaris use several breakpoints (Appendix D).

**L7. At the switch, decide per region: keep, resize, swap or drop. Draw phones as 390-wide `Mobile/` screens, never resized desktop frames.** A region that cannot fit should change form. *GAIDS:* below 992 the tab group, deployment chips, Publish and cost leave the top bar; the rail becomes a drawer; menus and dialogs become `Mobile/Sheet` with 48px rows; sub-tabs scroll sideways; `Mobile/Run Bar` carries cost and Run; two-column rows stack; gutters are 16 (content 358). Restructured patterns are re-made as `Mobile/*` components (`Mobile/Tool Row`), not shrunk. **[gap]** `Mobile/Topbar` is 61 high (60 plus its 1px rule), code 56. *Refs:* Material, Fluent, Astryx, Primer.

**L8. Design at one density, the compact default, with one control height per row.** Mixed heights in a row read as mistakes; modes multiply states. *GAIDS:* `Button` default 36 (padding 0/12, gap 8, radius 8); phone rows 48. **[gap]** heights are drawn, not tokenised: small `Button` is 28, 24, 22 or 20 by kind; Tab top and Menu Item 33, Tab middle 35, `Input/Search`, `Input/Select` and `Input/Number` 39, `Input/Control` 50; code form controls 40, top bar 36. *Refs:* Astryx, Carbon, Stripe, Polaris.

---

## 6. Shape, borders and elevation

**S1. Pick radius by role from the six `radius/*` tokens, never by eye, and draw no pill shapes.** Matching radii make related shapes a family. *GAIDS:* `tiny` 4 (small `Button`, badges and the smallest labels); `small` 8 (default Button, inputs, rows, menu items, tabs, tooltips, tags, chips and controls up to 36 tall); `regular` 12 (containers holding controls: Menu Shell, Tab Group, `Settings/Section`); `big` 16 (`Workspace/Pane`, `Modal/Dialog`, workflow and About cards); `full` 99 (avatars, radio and check circles, dots); `compact` 6 per L3. **[gap]** `RunStatus/Chip` is a 99 pill and `Copilot/Follow-up Chip` is 12; literal radii equal a token on `Input/Checkbox` (4), `Tab` low (8), `Progress` (99), `Knowledge/File Row` (8) and `Integrations/*` (4); `Composer/Bar` WhatsApp still binds the deleted `radius/huge`; code ships 8/10/12/16/32/99 **[open]** code names (Appendix C #12). *Refs:* Atlassian, Spectrum, Material, Fluent.

**S2. Keep nested corners concentric: inner radius equals outer radius minus the padding between, and a child never exceeds its parent.** Uneven corner gaps look wrong at a glance. *GAIDS:* Menu Shell 12 with 4 padding holds 8px rows; Tab Group likewise. **[gap]** `Composer/Bar` Builder is a literal 20 around 8px buttons on 8 padding (concentric is 12). *Refs:* Astryx, Material, Spectrum, Polaris.

**S3. Draw every border as a 1px inside stroke, and change its colour, not its width, for state.** One width keeps edges quiet. *GAIDS:* `line/soft` for containers, menus, cards and dividers; `line/strong` for hover and selected edges; 2px only on the Slider knob and the focus ring (A4). `line/default` is what inputs, secondary Button, Tag and checkbox use today; it is decorative-grade at 1.49:1 on `bg/page` and fails A2 (Appendix C #2), so do not copy it onto new controls whose border is their only edge. *Refs:* Spectrum, Carbon, Atlassian (one default border width); Atlassian and Spectrum also widen to 2px for selection and focus, which GAIDS reserves for focus.

**S4. Reserve shadow for what lifts or floats. Use one named `Elevation/*` style per surface; never type a shadow.** Flat content plus one floating layer keeps depth meaningful. *GAIDS:* target is none at rest on cards, rows or sections. Drawn today: `Elevation/1 Raised` (black 6%, y1, blur 2) on active Tab, Tab Group and `About/Card` hover; `Elevation/2 Floating` (7.5%, y2, blur 4) on `RunStatus/Chip` and `Chat/New Chat FAB`; `Elevation/3 Overlay` (10%, y1, blur 5) on menus, tooltips, `Modal/Dialog` and `Mobile/Sheet`; `Elevation/Button Shadow` (5%, y2, blur 8) on secondary Button, `Workspace/Pane` and `Shell/App Shell`; its Hover partner (12%) on Button hover and the Switch knob; the inner `Right border subtle` on the rail and shell. **[open]** `Elevation/2` and all values are absent from the written spec (Appendix C #10). **[gap]** literal shadows on the Slider knob and Workflow Badge; code has about 20 shadow recipes and no tokens. *Refs:* Atlassian, Carbon, Spectrum, Polaris.

**S5. Make every menu a bare wrapper around `Overlay/Menu Shell`. Never put a shadow, border, fill, radius or padding on a menu instance.** The surface then changes once, in the shell. *GAIDS:* standing rule. Shell is `bg/page`, 1px `line/soft`, `radius/regular`, `space/1` padding, `Elevation/3 Overlay`; select lists use it too. *Refs:* Atlassian, Carbon, Spectrum.

**S6. [open] Do not rely on a black shadow alone to separate surfaces in Dark; pair it with tone or a hairline.** *GAIDS:* the `Elevation/*` shadows are black at 5 to 12% and not mode-aware, nearly invisible on the Dark page; menus keep a hairline but `Modal/Dialog` has no border (Appendix C #10). *Refs:* Atlassian, Spectrum, Apple, Material.

**S7. Stack panes, rail and side panels, then menus and tooltips, then scrim with dialog or sheet. Anything opened from a dialog floats above it.** A fixed order avoids surprise overlaps. *GAIDS:* the Report dialog's reason select is the one menu over a modal. *Refs:* Fluent, Primer, Atlassian.

**S8. Dim the screen with `bg/scrim` behind every modal dialog, bottom sheet and full-screen drawer. Give menus and tooltips no scrim.** Modals block the page; popovers do not. *GAIDS:* `bg/scrim` is 50% Light, 75% Dark, covering the whole frame including the rail; the dialog is `bg/page`, `radius/big`, `Elevation/3 Overlay`, no border; sheet top corners 16. **[gap]** code scrim is 30%. **[open]** production sheets use 32. *Refs:* Primer, Material, Atlassian, Fluent.

---

## 7. Iconography, imagery and logos

**I1. Use Font Awesome Regular for every icon unless you can state the reason for another style.** One style keeps stroke weight even in dense screens. *GAIDS:* default `Icon/Regular/<name>`; the one recorded Solid exception is the Eco glyphs `cloud`, `droplet`, `bolt`; do not delete existing Solid components. **[gap]** about 3% of Playground icon instances are Solid (`check`, `plus`, `brackets-curly`, `arrow-right`), and some library components draw a non-Regular glyph themselves (`Input/Checkbox`, `Avatar` fill=Icon, `RunStatus/Chip` marker, `Chat/Message Actions`, `Chat/Sources Toggle`); code uses about nine Solid icons for every ten Regular. *Refs:* Carbon, Polaris, Fluent, Atlassian.

**I2. Place icons only as `Icon/<Style>/<name>` instances; never draw, trace or paste a glyph.** Hand-made copies drift from the Font Awesome Pro 7 kit the app ships. *GAIDS:* 16x16 components, fill bound to `icon/primary`; add missing glyphs with the `gooey-fa-icons` skill. *Refs:* Spectrum, Stripe, Atlassian.

**I3. Size an icon to its text: 16 beside 14px text, 12 beside `Meta`, 20 in dialog headers and glyph tiles.** A changed ratio makes rows look uneven. *GAIDS:* 12 in `Tag` and small `Button`, 16 in default `Button`, 20 in the dialog header. **[open]** 14 is used in `Nav/Item`, the picker metric chips, `Chat/Message Actions`, stat cards and 28px avatars. **[gap]** about 6% of instances are off-step (12.6, 11, 10, 9.6); code has no icon-size tokens. *Refs:* Carbon, Atlassian, Primer, Polaris.

**I4. Colour an icon with the `icon/*` token matching its text's rank; status icons keep status tokens.** Icon ink can then change without touching text. *GAIDS:* `icon/primary`, `icon/secondary`, `icon/tertiary`; `status/*` or `run/running-ink` for status; `action/on-primary` on filled controls; `icon/muted` only for decorative or labelled icons. *Refs:* Carbon, Stripe, Primer, Spectrum.

**I5. Pair an icon with a visible label unless the action is universal, and give every row of a menu or list an icon or none.** Few glyphs read alone, and mixed rows look broken. *GAIDS:* the icon sits left of its label (`Overlay/Menu Item`, `Mobile/Sheet Item`); icon-only is for close, kebab, back, menu, paperclip and microphone. Icon-only controls need a name and tooltip (A10). *Refs:* Polaris, Atlassian, Primer, Carbon.

**I6. Give each icon one meaning and keep it everywhere.** A glyph with two meanings invites wrong clicks. *GAIDS:* `leaf` eco, `shield-check` zero data retention, `circle-dollar` price (plain `coin` was rejected for price), `brackets-curly` variables, `books` sources (only a Light-style glyph exists), `xmark` close. **[open]** the funds bubble draws `circle-dollar` for a balance; Appendix C #23 proposes `coin` for balance. *Refs:* Carbon, Polaris, Atlassian, Apple.

**I7. Never use emoji as icons, headings, status marks or button labels.** Emoji vary by platform and clash with the icon set. *GAIDS:* standing rule. **[gap]** 295 emoji uses in 66 Python files; `Copilot/Follow-up Chip` draws emoji plus label. *Refs:* Polaris, Primer.

**I8. Place logos as `Logo/<Brand>` instances at a set size; never recolour or redraw them.** A changed mark misrepresents its owner. *GAIDS:* sizes 16, 20, 24, 32, 48; one-colour marks bind `text/primary`, brand-colour marks stay literal in both modes; the source is lobehub/lobe-icons, so ask before downloading more. `Workspace Logo/<Org>` is placeholder art. *Refs:* Spectrum, Fluent.

**I9. Use `Avatar` at 20, 28 or 64; circle for a person, Rounded for an agent, team or workspace.** Shape separates entities before anyone reads. *GAIDS:* **[proposal]** `Avatar` has both shapes but no written meaning. **[gap]** the 36px avatar in `Topbar/Bar` is a plain frame, outside the three sizes. *Refs:* Primer, Atlassian.

**I10. Do not decorate: no sparkles, mascots, characters or illustration in empty, loading or error states.** The brief names decorative AI an anti-reference; one line plus starters teaches faster. *GAIDS:* empty states are an icon, one line of text and at most three starters (`Tools/Empty State`); errors use a coral `triangle-exclamation`; `Brand/Gooey Bot` is a logo mark, not a character. **[open]** `sparkles` is drawn as a meaning glyph (Best match, thought rows, Ask Gooey), and the Eco frames hold five illustration PNGs (Appendix C #16). No glow, glass or gradient either (AI2). *Refs:* Primer (plain alert icon for errors), Spectrum (no gradient illustration on errors), Atlassian (flat colours, no gradients or blurs); the ban on illustration in empty states is GAIDS's own (PRODUCT.md).

---

## 8. Motion

GAIDS has no motion spec in Figma and no motion tokens in code: about 11 distinct durations (80 ms to 2.4 s) and 7 easings ship, roughly two dozen duration-and-easing pairs. Nothing in this section is approved except the existing code values it describes.

**M1. [proposal] Add motion only to show a state change, confirm an action or keep people oriented; if removing it loses nothing, remove it.** Quiet by default covers movement as well as colour. *GAIDS:* loop only for a live state (running dot, skeleton pulse, thinking-line shimmer); never flash more than three times a second. *Refs:* Atlassian, Apple, Polaris, Primer.

**M2. [proposal] Use three durations and two curves: `fast` 100 ms for hover, press, menus and tab switches; `base` 200 ms for panels and sheets; `slow` 300 ms for dialogs; an exit takes the next step down.** Frequent motion must not slow work, and eleven durations make surfaces feel unrelated. *GAIDS:* the steps round code's clusters (80 to 120, 150 to 200, 240 to 300 ms) and are our own, not a reference value; `ease` for state change, `cubic-bezier(0.22, 1, 0.36, 1)` (already `--pane-ease`) for anything that travels, `linear` only for spinners, no bounce. Overlays move from the edge they belong to (phone sheets rise from the bottom, the rail becomes a left drawer); dialogs fade in place, replacing `popOut`. **[gap]** outliers: the 1 s `fadeInBackground` scrim and `popOut` scaling from 0.5. Names are suggestions. *Refs:* Atlassian (durations by frequency, exits 50 to 100 ms shorter), Material (exits faster, overlays from their edge), Fluent, Carbon (easing).

**M3. [proposal] Specify a reduced-motion state for every animation: swap movement for an instant change or a short fade, stop decorative loops, and pair every animation with static text or shape.** Movement can make people ill, and meaning carried by motion alone is lost. *GAIDS:* `RunStatus/Chip` Running has a label and teal border beside its pulse; code covers reduced motion in 7 CSS blocks. **[gap]** not covered: `scroll-behavior: smooth`, `popOut`, `fadeInBackground`, `gui-video-shimmer`, the `spin` loader and `fa-spin` / `fa-beat`. **[open]** whether a small loader may keep turning (Primer and Atlassian allow it; Apple and Material are silent on loaders, and Apple says a stalled indicator reads as a hang). *Refs:* Apple, Material, Primer, Atlassian.

---

## 9. Accessibility and inclusion

Target: WCAG 2.1 AA (`PRODUCT.md`, `DESIGN_TOKENS.md`). **[2.2]** marks a WCAG 2.2 addition worth adopting early (see Appendix C). Contrast numbers and every failing pair are in Appendix A.

**A1. Check each text token against the surface it sits on: 4.5:1 for text and 3:1 for large text (24px, or 18.66px and bold); write the ratio and background beside any colour you add.** Passing on `bg/page` does not mean passing on `bg/panel`. *GAIDS:* only `Display`, `Heading/H1` and `Heading/H2` count as large; `Heading/H3` to `H5` need 4.5:1. `text/primary` and `text/secondary` pass everywhere in Light; `text/tertiary` passes only on `bg/page` and `bg/input`; `icon/muted` is for decorative or already-labelled icons. **[gap]** see Appendix A. *Refs:* Apple, Material, Fluent, Carbon.

**A2. Give icons, control borders and state indicators 3:1; an input whose border is its only edge needs a 3:1 border.** Low-vision users cannot find a control they cannot see. *GAIDS:* `line/soft` and `line/default` are decorative (`line/default` on `bg/page`: 1.49 Light, 2.25 Dark); `line/strong` reaches 3:1 in Light on `bg/page` and `bg/surface` only. **[gap]** `Input/Control` and `Input/Checkbox` have no 3:1 edge today. *Refs:* Material (outline 3:1), Fluent (non-text 3:1), Carbon (UI components 3:1; it holds icons to 4.5:1), Polaris (storefront guidance).

**A3. On Dark `bg/surface` and `bg/panel`, set message text in `text/primary` or `text/secondary` beside a coloured icon, not in `status/danger` or `brand/gooey-blue`.** Status colours thin out first in Dark. *GAIDS:* `status/danger` is 3.67 and 3.07 there, `brand/gooey-blue` 4.37 and 3.66; `Chat/Error Bubble` already follows this. *Refs:* Apple, Fluent, Carbon.

**A4. Draw a visible focus state on every interactive component, and never remove an outline without replacing it.** Keyboard users cannot otherwise see where they are. *GAIDS:* **[gap]** only the Input family has `state=focus`, a border change to `line/strong` with no ring; Button, Tab, `Nav/Item`, `Overlay/Menu Item`, Checkbox and Switch have none; Slider's `state=hover` doubles as focus with a teal 4px halo at 15%, far below 3:1; code has 7 `:focus-visible` rules against 11 `outline: none`. **[proposal]** one 2px ring with a 2px outside offset and a role token `focus/ring` aliasing `brand/gooey-blue` (3:1 or better on page, surface and panel in both modes), never `action/primary`, which means selected. The Guided one shot frame `760:27870` draws the ring flush against the control; its label says 2px offset, which is not drawn. *Refs:* Material, Atlassian, Carbon, Primer.

**A5. Make every task keyboard-operable with native roles: Tab moves between groups, arrows inside them, Enter or Space activates, Escape closes the top overlay.** Keyboard and switch users cannot use pointer-only controls. *GAIDS:* `Tab Group`, `Overlay/Menu Shell` menus, `Nav/Sidebar Rail`, the model list. **[gap]** code has no arrow-key handling beyond `@reach/tabs` and `react-select`; `GooeySwitch` is a hidden input with no `role="switch"`. *Refs:* Material, Carbon, Polaris, Primer.

**A6. Keep tab order equal to visual order, start the app with a skip-to-main link, and keep the focused control clear of sticky bars.** Focus never moves unless the person acts. *GAIDS:* **[proposal]** skip link in `Shell/App Shell`; **[2.2]** check `Mobile/Run Bar`, `Composer/Bar` and sticky modal footers. *Refs:* Carbon, Spectrum, Polaris, Primer.

**A7. Move focus into every dialog, menu and sheet on open, trap it, and return it to the trigger on close.** Without moved focus, keyboard and screen-reader users do not know something opened. *GAIDS:* `Modal/Dialog`, `Overlay/Menu Shell`, `Mobile/Sheet`. **[gap]** server `gui.alert_dialog` has no `aria-modal`, name, trap or restore; the React `MediaTags` traps and restores focus. *Refs:* Material, Fluent, Carbon, Primer.

**A8. Never hide help or actions behind hover; show them on focus and tap, and keep tooltips for one short sentence that explains a control or metric, never for errors or required information.** Touch and keyboard users cannot hover, and tooltips stay hidden until asked for. *GAIDS:* `Overlay/Tooltip` hangs off info glyphs, which must be focusable buttons ("Higher values take more risks"). **[gap]** `GooeyHelpIcon` has no `tabIndex` or name and opens after 1.2 s, not on touch. *Refs:* Atlassian, Fluent, Primer, Stripe.

**A9. [2.2] [proposal] Give every interactive element a hit area of at least 24 by 24 px (enlarge the hit area, not the drawn size), and offer a non-drag path for anything draggable.** Tremor, touch and pointer imprecision make small targets easy to miss. *GAIDS:* `Button` stays 36 and phone sheet rows 48, as decided (no 44px rule). **[gap]** under 24 today: small icon Buttons (20, 22), small ghost Button (22), Switch (20 and 18 high), Checkbox (16), Slider thumb (18), `Chat/Activity` collapsed (21), `Chat/Sources Toggle` (20), `Chat/Message Actions` (14); the 10px sidebar resize grip is mouse-only. Sliders show a typeable value and `Knowledge/Drop Zone` keeps Add a link. *Refs:* Atlassian, Primer; touch guidance elsewhere runs 44 to 48 (Apple, Fluent, Carbon, Polaris, Material).

**A10. Name every icon-only control with its action, in Button's `label` property with `showLabel` off.** Screen readers and voice control read names, not glyphs. *GAIDS:* sentence case, verb first, no role word, row name included ("Delete {name}"); kinds `icon-primary`, `icon-secondary`, `icon-ghost` plus `Overlay/Tooltip`. Destructive actions are never icon-only. **[gap]** Python icon buttons have no name; Python icons never carry `aria-hidden`. *Refs:* Material, Fluent, Primer, Spectrum.

**A11. Pick heading level by structure, not by text style (one H1 per view, no skipped levels), and give images a text alternative that says what they add; mark decoration empty.** Screen readers navigate by structure and read alternatives, not pixels. *GAIDS:* `Heading/H1` to `H5` are looks only; a provider logo beside its name is decorative. **[gap]** code renders control labels as h1 to h6 and names the logo "Gooey.AI" in three places and "Gooey Logo" in one. Add annotations only when the owner asks. *Refs:* Material, Atlassian, Primer, Apple.

**A12. [proposal] Announce progress and state in text, politely: that a reply is in progress and when it ends (never the partial text), run state with its label, failures assertively; never move focus into the transcript, never auto-dismiss an error, warning or anything with an action, and give runs that take minutes a persistent labelled status with Cancel.** A live region repeating streamed text buries everything else; people read at different speeds. *GAIDS:* `Chat/Bot Bubble` (`thinking`) marked busy until done; every `RunStatus/Chip` state has a label; `Chat/Error Bubble` `kind=error` is the one assertive message, `kind=funds` and `Settings/Notice` are polite with the action as the next tab stop; `Chat/Activity` is one button with `aria-expanded` and a name carrying the summary. **[gap]** the app has no `aria-live`, two `role="status"` and nothing on run progress; `gui.error` and `gui.success` carry no role; code reverts "Link copied" after 2 s; if a toast is ever drawn, errors and actions persist and hover and focus pause it. *Refs:* Primer, Carbon, Fluent, Polaris.

**A13. Let text grow to 200% without clipping, and reflow to a 320px column at 400% zoom with no sideways scroll.** People enlarge text and zoom; clipped or sideways-scrolling text is lost. *GAIDS:* phone frames are 390 wide; check one at 320. Wrapping copy takes `Body/*` (150%); `UI/*` and `Meta` (120%) stay on one line. **[gap]** default `Button` is a fixed 36 high with 0 vertical padding; specify `min-height`. *Refs:* Apple, Material, Fluent, Primer.

**A14. Give every field a visible, persistent label and keep help in visible text; show errors next to the field, in words, with the fix; on a failed submit, focus the first invalid field.** Colour or an icon alone is not a message. *GAIDS:* `Input/Text Field` stacks label (`UI/Large`), `Input/Control` and help (`Body/Body`). **[gap]** the Input family has no error state; code hides help in an info icon with a tooltip (98 `help=` uses). **[proposal]** `state=error`: `status/danger` border and icon, message in `text/primary`, `aria-invalid`. *Refs:* Atlassian, Polaris, Primer, Fluent.

**A15. Prefer an enabled control that explains itself; if you must disable one, give the reason in visible text beside it, and use one disabled treatment.** Disabled controls leave the tab order and cannot explain. *GAIDS:* **[gap]** Button dims to 0.5 and inputs, checkbox and text field to 0.65 (literals, exempt from contrast); the Switch has disabled tokens; the follow-up chip uses `text/tertiary`. **[open]** one opacity, recommended 0.5 (Appendix C #6). *Refs:* Atlassian, Primer, Spectrum.

**A16. Write for the least expert reader and use inclusive language: plain words, abbreviations spelled out on first use, people-first wording, no ability assumptions, describe actions rather than positions ("see below", "on the left"), varied people in mock data; no dialog opens another dialog.** Plain, literal text serves translation, screen readers and tired people alike. *GAIDS:* PRODUCT principle 5; ZDR is zero data retention and CO₂e is carbon dioxide equivalent, so each needs a visible expansion nearby and the full term in the accessible name; the `/1M` in price strings reads as per million tokens, to confirm with the owner. *Refs:* Apple, Fluent, Atlassian, Carbon.

**A17. Design text slots for strings 50% longer than English, format dates, numbers and currency by locale, and plan for non-Latin scripts.** Translations grow, and Hindi is a named user need. *GAIDS:* model-picker chip slots are fixed (56, 124, 76), so test long model and region names. **[open]** Inter and Domine are Latin only and no Devanagari fallback is chosen (T12); right-to-left is out of scope until the owner decides (Appendix C #20). *Refs:* Material, Fluent, Carbon, Atlassian.

---

## 10. Content and voice

Voice is precise and friendly: numbers are exact, language is plain, with expert confidence and no cold enterprise heaviness (`PRODUCT.md`). Placement and behaviour of messages are in section 11. Quoted strings are examples from Playground drafts and need sign-off; only the Report copy is approved.

**W1. Write plain, exact, friendly copy: short sentences, everyday words, address the reader as "you", and no idioms, slang, jokes, hype, "just" or "easy".** Exact facts earn confidence, and literal text translates. *GAIDS:* target the newer React voice ("Upload failed. Try again."); examples are global ("Build an agent for farmers in Kenya"). **[gap]** legacy Python copy says "Doh!" and ":(" and uses "Please" on about 130 lines. *Refs:* Polaris, Carbon, Spectrum, Primer.

**W2. Write new labels, titles, tabs, buttons and menu items in sentence case; capitalise only proper nouns and product names. Avoid all caps.** Nobody has to judge which words matter. *GAIDS:* "Choose a model", "Max output tokens"; "Ask Gooey" and "Gooey.AI" keep capitals; component names are not copy. **[gap]** Figma still has "Last Run Cost & Environment Impact" and an "LLM Instructions" tab; server code is mostly Title Case. **[open]** Home overlines are uppercase with no style; sentence case was proposed as a call "you may revisit", so confirm it. *Refs:* Carbon, Fluent, Material, Primer.

**W3. Start every button and menu action with a verb, and add the object unless the verb stands alone (Cancel, Run, Done, Publish, Save, Try again): "Add integrations", "Use model". Never use "OK", "Submit" or "Yes".** The label names the outcome. *GAIDS:* footers read Cancel plus "Use model" or "Send report"; phone copy says "Choose files". **[gap]** code has "Save and Run" and emoji-prefixed labels. *Refs:* Polaris, Primer, Atlassian, Carbon.

**W4. Name each concept with one word, everywhere, and do not coin names.** Each synonym is one more thing to learn. *GAIDS:* until the owner decides (Appendix C #21), use "agent" in copy about editing and running, and "workflow" only where the Report menu and `Workflow/Card` already say it (PRODUCT.md also says "recipe"); "model", never "LLM" in builder-facing labels; "Sign in" and "Sign out" **[open]** (Figma and code say "Log out" and "Login"); money words **[open]** (funds, credits, dollars, "Cr"). *Refs:* Polaris, Carbon, Spectrum, Apple.

**W5. Name settings and metrics by what they do, and expand abbreviations as A16 says.** Plain words are PRODUCT principle 5. *GAIDS:* "Intelligence", not "AA"; label a slider "Creativity" and put "sampling temperature" in help text. *Refs:* Carbon, Material, Atlassian, Spectrum.

**W6. Leave labels, titles, buttons and one-sentence help without a full stop; use no exclamation marks, emoji or ampersands, and write the … character, not three dots.** These marks add noise and translate badly. *GAIDS:* no emoji in UI copy. **[gap]** code ships "Saved!", emoji in 66 Python files and ASCII "..."; Figma strings such as "Thinking..." do too. *Refs:* Polaris, Primer, Material, Atlassian.

**W7. Draw mockups with real copy, icons and logos, never placeholder bars; label invented data and flag new copy for sign-off.** Fake content hides layout problems. *GAIDS:* house rule; invented numbers are logged in `GAIDS_CHANGELOG.md`; only the Report copy is approved. *Refs:* standing rule; Stripe (demo content labelled, no placeholder tabs).

**W8. Write digits with thousands separators and a space before the unit, one format per quantity; say "about" or give a range for estimates.** Exact numbers earn trust; false precision loses it. *GAIDS:* "$0.10", "670 mg CO₂e" then "1.1 g CO₂e" (change unit at its threshold), "5 g/M"; Eco shows ranges and "{confidence} confidence"; compact durations in chips ("Thought for 6s") are the one exception to the space. **[gap]** code ships "Cr", "~" and "≈"; the Eco modal frames draw "373 gCO₂e per kWh" and "≈", and `Chat/Balance Strip` draws "~$0.04", all against this rule; price strings write "$2 → $10 /1M" while eco figures write "/M". *Refs:* Polaris, Spectrum, Atlassian, Apple.

**W9. Write dates as short names without ordinals ("Sep 22"), show relative time for history, and let the locale format them.** Date and number order differ by locale, Hindi included. *GAIDS:* "Released Sep 22"; dates sit in `Meta` at the row end, with the exact time on hover; durations are compact in chips ("Thought for 6s") and spelled out in sentences. *Refs:* Atlassian, Polaris, Primer, Spectrum.

**W10. Write errors in three parts: what happened, why if known, what to do next. Blame no one; skip "please", "oops" and codes; name the thing that failed.** People need a next step, not a verdict. *GAIDS:* `Chat/Error Bubble` copy ("That's a setup issue, not something you did.", "Your agent has not been changed"), a Try again button, raw text behind "Technical details". **[gap]** code shows raw exceptions; the Ask Gooey error frame says "on our side" instead of naming what failed. *Refs:* Atlassian (what happened, consequence, how to proceed; it uses "we" for system faults, which GAIDS avoids), Polaris, Primer, Spectrum, Carbon, Apple.

**W11. Title a confirmation with the action, say what it affects and whether it can be undone, and repeat the verb on the confirm button; after success say what changed in past tense ("Link copied", never "Success!").** "Are you sure?" adds nothing. *GAIDS:* code already pairs "Delete" with a consequence sentence; drop "Are you sure". **[gap]** no confirmation dialog is drawn yet. *Refs:* Primer, Spectrum, Carbon, Atlassian.

---

## 11. Patterns

Only patterns GAIDS has or needs. Wording of messages is in section 10; AI-specific surfaces are in section 12.

**U1. Start every desktop page from `Shell/App Shell`; keep destinations in the rail and page actions in the top bar, with one primary there: Run, at the far right.** Constant chrome keeps people oriented; navigation in two places blurs hierarchy. *GAIDS:* `Nav/Sidebar Rail` and `Topbar/Bar` (56 tall) holding `Tab Group`, `Topbar/Deployment`, `Topbar/Eco Cost`, Publish (secondary) and Run (primary). Workspace and account items live in `Nav/Account Menu` and `Nav/Workspace Switcher`; workflow items (Report) on the title block menu; Terms and Privacy under `Nav/Learn More Menu`; Log out last (drawn as "Log out"; W4 leaves Sign out open). **[open]** Terms and Privacy URLs and the Cookie settings home are not set. *Refs:* Spectrum, Carbon, Material, Atlassian.

**U2. Use `Tab` for three jobs: top switches page views, middle switches panels in a pane, low re-sorts a list. Two levels is the ceiling; strips never wrap.** *GAIDS:* top is `Tab Group` (About, Edit, Preview, Split, Usage); middle is the strip in each `Workspace/*Panel` and `Mobile/Edit Tabs`; low is Recommended, Smartest, Greenest, Cheapest. **[gap]** `low` radius is a literal 8. *Refs:* Primer, Spectrum, Atlassian, Polaris.

**U3. Use the lightest surface that holds the task: tooltip, menu, in-pane content, then dialog. One dialog at a time; a menu may open over it.** Heavier surfaces cost focus. *GAIDS:* `Overlay/Tooltip`, `Overlay/Menu Shell`, `Modal/Dialog` in the house format (52px header, hairlined footer, primary at right). *Refs:* Atlassian, Fluent, Apple, Carbon.

**U4. [proposal] Group settings by capability: switch, title and summary in the `Settings/Section` header, fields inside the same card, only while on.** Dependent fields belong beside what enables them. *GAIDS:* the Settings tab is an unapproved Playground design that the owner marked a call to revisit; `kind=capability` opens fields under a hairline, two per row at most; `kind=group` uses a chevron. *Refs:* Polaris, Primer, Carbon, Atlassian.

**U5. Put labels above controls in one column, write "(optional)" in the label of optional fields, and never use a placeholder as the label.** Top labels scan fastest and keep one left edge. *GAIDS:* `Settings/Field` (label `UI/Regular`, `description` in `Body/Small`, `control` slot); phone fields are one column at 358. Essential hints go in the description; `showInfo` tooltips are extras. *Refs:* Carbon, Atlassian, Fluent, Spectrum.

**U6. Give each page one save model: everything saves as it changes, or one Save commits the page. Never put a `Switch` beside its own Save.** Mixed models leave people unsure what is stored. *GAIDS:* phone shows unsaved changes as a dot on the Save square (`Mobile/Topbar` `showDot`); no desktop equivalent is drawn. **[open]** see Appendix C. *Refs:* Primer, Polaris, Fluent, Carbon.

**U7. Validate a field when the person leaves it, then as they type so the error clears when fixed. End a form with one primary Button named for the outcome at the right, Cancel beside it, enabled until submit.** Early errors punish typing; a disabled button explains nothing. *GAIDS:* **[gap]** `Input/Control` has no error state (**[proposal]** see A14); code validates once, form-level, on Run, and its login form disables submit until filled; footers pair Cancel (secondary) with Send report, Use model, Done or Add funds. *Refs:* Carbon, Atlassian, Fluent, Primer.

**U8. Show list and detail together so a choice is made in one pass; give every row the same facts in the same order and slot widths, and preselect one recommendation with a plain reason.** Leaving to research a choice is the failure (principle P4); columns scan only if they line up. *GAIDS:* `Choose a model` **[proposal; not a component]**: list 480 on `bg/page`, detail on `bg/surface`, footer summary, Cancel, Use model; Intelligence, Hosting, Eco, Price in fixed slots (56, 124, 76); "Best match" balances all four inside active filters and is the only ink pill. **[open]** "Best match" is not explained in any frame. *Refs:* Material, Primer, Polaris, Astryx.

**U9. [proposal] For multi-select, apply selection live, show the running count beside one Done button, and offer Select all on long lists.** There is no staging step to forget. *GAIDS:* `Integrations/Picker` with `Integrations/Tool Row` is an unapproved Playground design; the unit is a tool, so apps expand; footer "3 tools selected" and primary Done. **[gap]** `Overlay/Menu Item` has no selected state; the Tools trigger menu hand-draws a check. *Refs:* none; GAIDS's own pattern (Spectrum's bulk-action bar and Primer's explicit-save multi-select point the other way).

**U10. Say what a search matches in its placeholder, call narrowing a list "filter", show active filters as removable chips with one Clear control, and when nothing matches name the filters and offer to remove each.** People must see why a list is short. *GAIDS:* `Input/Search` (39 tall), "Search apps or categories"; "No models match EU, ZDR and Open-source" with Clear filters; `Integrations/No Results`. **[gap]** no filter chip, no clear button in `Input/Search`, no result count; the picker's search row is not on `Input/Search`. *Refs:* Primer, Spectrum, Polaris, Carbon.

**U11. Use the lightest feedback that works: a label swap, `Settings/Notice`, an in-flow message, then a dialog for blocking decisions. Add no toast.** Match interruption to importance. *GAIDS:* no toast, banner or snackbar exists in Figma or code; code swaps a control to "Link copied" for 2 s; `Settings/Notice` info is `bg/panel` + `line/soft`, warning is `run/warn-bg` + `run/warn-line`. **[open]** whether a toast or banner joins (Appendix C #14). *Refs:* Primer (no toasts); Fluent, Atlassian and Carbon share the lightest-first ladder but still ship a toast or flag, which GAIDS omits.

**U12. Show a status chip only when the status needs a decision or is changing: one status per object, one or two words, always with its marker.** A chip on everything is noise. *GAIDS:* `RunStatus/Chip` (Running teal, Warning amber, Error coral, Idle and Success neutral). **[gap]** variant names differ from on-screen labels (Queued, Completed, Cancelled, Failed); code shows no chip for finished runs. **[open]** keep Completed? *Refs:* Carbon, Spectrum, Polaris, Primer.

**U13. Match the loading indicator to the wait: none under about 1 s, indeterminate for 1 to 3 s, determinate with a label beyond. Keep the chrome and load inside it, with skeletons at final size.** A flash is worse than a short wait; no blank page, no layout shift. *GAIDS:* `Progress` atom (five values, no continuous width); agent waits use `ToolCall/Thinking Line` (AI11); skeleton rows (two `bg/selected` bars) are not yet a component. **[gap]** no spinner component; code has seven loading idioms. **[proposal]** a Spinner atom and a skeleton row. *Refs:* Fluent and Primer (the 1 s and 3 s thresholds, as does Atlassian); Polaris, Stripe and Material (skeletons, no layout shift). References put the spinner threshold between 200 ms (Stripe) and 3 s (Carbon); GAIDS follows Fluent and Primer.

**U14. Give each empty view its cause and one next action in a line of text, with at most three one-tap starters; say what is missing and why, use a different message when filters hide everything, and no illustration.** Empty is a teaching moment, and starters teach by doing; if a tour is ever added it must be optional, short and dismissible. *GAIDS:* `Tools/Empty State`, `Knowledge/Drop Zone`, `Integrations/No Results`; "No tools yet" with three starter chips; the Ask Gooey splash teaches in place ("Edit this agent with AI"); a failed load is an error, never an empty state. **[gap]** no shared Empty State component; code shows text only. **[proposal]** one `Empty State` with a cause variant. *Refs:* Carbon, Atlassian, Polaris, Primer, Stripe (cause plus one action; each of Atlassian, Polaris, Primer and Carbon also draws an illustration, which GAIDS omits by PRODUCT.md anti-reference; "at most three starters" is GAIDS's own).

**U15. Show an error where the answer would have appeared, as a full-width system message with four 12px corners; offer a way forward, keep the person's work, and show "Add funds" only when a run is blocked, never inside a normal reply.** Errors away from their cause get missed; dead ends and lost input cost most; selling through the assistant erodes trust. *GAIDS:* `Chat/Error Bubble` kind error (`run/error-*`) or funds (`run/warn-*` with `Chat/Balance Strip`), no bot tail, `actions` slot; "Ask Gooey for help" primary for deterministic errors, "Try again" always, and only Try again inside Ask Gooey. **[gap]** it still nests the deprecated `Chat/Reasoning Toggle`. **[proposal]** retry-first errors (provider busy, rate limit, offline) and "Ask an admin" are undrawn. *Refs:* Polaris, Fluent, Primer, Atlassian.

**U16. Make destruction a danger row placed last under a divider (red ink and icon, no red fill, no red Button); match friction to impact; warn before closing anything that holds unsaved work.** Position and a clear verb do the work, so red stays rare; over-confirming trains click-through. *GAIDS:* `Overlay/Menu Item` and `Mobile/Sheet Item` `kind=danger`; reversible removals use undo or nothing; irreversible ones get a confirm naming the object, with the primary repeating the verb; type-to-confirm only for wide impact. "Remove" means the object survives, "Delete" means it is destroyed. **[gap]** no confirm dialog or unsaved warning is drawn on desktop. *Refs:* Primer, Fluent, Polaris, Spectrum.

**U17. On a phone give each desktop region one home: rail in a drawer, views and actions in the kebab sheet, cost and Run in a sticky bar; turn every menu and dialog into a `Mobile/Sheet` and never hide an action behind hover or drag.** Regions need a place, not a squeeze; touch has no hover. *GAIDS:* `Mobile/Topbar` (menu or back, title with crumb, kebab, one 36px square: Preview on About, Save elsewhere); `Mobile/Run Bar`; `Mobile/Sheet` radius 16 (production ships 32 **[open]**) with `pressed` rows; `Button` stays 36; copy says "Upload ..." or "Choose files". Breakpoint rules are L6 and L7. *Refs:* Material, Primer, Fluent, Polaris.

---

## 12. AI and agent experiences

Gooey users build agents and also watch them run, so every AI surface has two jobs: show what the system is doing, and keep the person in charge. Where references show AI with glow, gradients or a dedicated colour, `PRODUCT.md` wins.

**AI1. Give user messages, AI replies and system notices three distinct containers, and show reasoning and tool use as a muted line, not a bubble.** People must always know who or what is speaking. *GAIDS:* `Chat/User Bubble` (`bg/panel`; `whatsapp/bubble-out` in the WhatsApp theme), `Chat/Bot Bubble` (`bg/page`), `Chat/Error Bubble` (full width, no bot tail), `Chat/Activity` (muted text, no box). *Refs:* Primer, Fluent.

**AI2. Identify AI with plain words and existing ink; never use glow, glass, gradients or a dedicated AI colour.** Decoration dilutes meaning; the brief names over-decorated AI an anti-reference. *GAIDS:* teal, amber and coral stay status colours; the accent stays `action/primary`. **[open]** `sparkles` marks "Best match", thought rows and Ask Gooey today (Appendix C #16). *Refs:* Atlassian (flat colours, no gradients or blurs), Polaris (the not-decoration principle). Carbon (aura and gradient border), Polaris (purple "magic" role) and Fluent (Copilot shimmer) show AI with a gradient or a dedicated colour, which GAIDS rejects.

**AI3. Name AI features by what they do and present the AI as software, not a person; state what it can and cannot do once, in the empty chat state, not under every reply.** Honest names build trust, and repeated disclaimers become noise for builders. *GAIDS:* "Generate with AI", "Ask Gooey", "Try again"; never "smart", "magic" or "intelligent" as a feature name (the model lens "Intelligence" is the one exception, W5); "Thinking" and "Thought for" are kept pending Appendix C #17; no human names or "I feel"; use `Brand/Gooey Bot` or `Brand/Builder Logo`. **[proposal]** one `Body/Small` `text/secondary` limits line on the Ask Gooey panel Empty state; copy needs sign-off. *Refs:* Spectrum (name by function), Fluent (explicitly digital; it requires a disclaimer on every response, which GAIDS rejects), Apple and Carbon (state purpose and limits up front), Atlassian (skip repeated AI disclaimers).

**AI4. Keep every AI-assisted task doable by hand, and let people close AI panels.** AI that blocks the manual path demands unearned trust. *GAIDS:* every Edit-tab field stays editable without Ask Gooey; the panel has a close control (a 32px plain frame today, not yet a `Button` `icon-ghost`). *Refs:* Apple, Carbon.

**AI5. Show cost and CO₂e together wherever a run starts or a model is chosen; list model facts in a fixed order and slots, explain each abbreviation once, and mark estimates as estimates with ranges and words, not numeric confidence scores.** Builders trade price against footprint in one pass, fixed positions let people compare, and a precise-looking guess breaks the exact-numbers promise. *GAIDS:* `Topbar/Eco Cost` (ghost `Button` holding `Topbar/Eco Readout`, dollars over CO₂e in `run/running-ink`) opens the Eco modal; phone uses `Mobile/Run Bar`; the picker lists Intelligence, Hosting (flag + ZDR shield), Eco (`leaf`, teal on `bg/ok-wash`) and Price, with one legend line for price, CO₂e and ZDR **[proposal]**; Eco figures carry ranges and a "How this is estimated" link. **[gap]** no missing-eco-data state exists; the picker is frames plus a `[stand-in] Model Picker/Model Row`. **[open]** funds vs credits wording. *Refs:* PRODUCT principles 2 and 5; Spectrum (cost as a plain fact in the plan's units); Apple and Fluent (estimates as concepts, not scores). No reference covers CO₂e.

**AI6. Say in specific words where data goes: region, retention and training use.** Vague data statements prevent real consent. *GAIDS:* the Hosting chip and region cards show region and ZDR at the choice; Terms and Privacy sit under Learn more. **[proposal]** one plain line under the Hosting options on retention and training; copy needs sign-off. *Refs:* Apple, Fluent.

**AI7. Confirm any action with real-world effect before it runs, naming what will happen.** Sent messages, spent funds, writes to connected apps and deletions cannot be undone. *GAIDS:* a confirm dialog with Cancel (secondary) and a verb button such as "Send report", never "OK"; destructive entries are danger rows, never a red `Button` (U16). **[gap]** no confirm dialog is drawn and `Modal/Dialog` has no header or footer slot. *Refs:* Apple, Polaris, Primer, Carbon.

**AI8. [proposal] Show each tool as an action the agent can take, with its trigger, one click from off; stage every AI change to an agent for review and offer Undo, never apply silently.** Autonomy means what the agent may do, when, and with which access; people stay accountable for what they publish. *GAIDS:* the Tools, Settings and Integrations structure is an unapproved Playground design: rows (`Mobile/Tool Row` on phone) carry name, description and a trigger select, and a capability card owns its `Switch`. Mark tools that change things outside Gooey with text, not colour. **[gap]** the "agent changed" confirmation with undo is one of ten undrawn Ask Gooey cases. *Refs:* Fluent, Polaris, Primer, Carbon.

**AI9. Swap Send or Run for Stop while work runs, keep partial output, and label it partial.** Stopping must be as easy as starting. *GAIDS:* **[gap]** `Composer/Bar` `action` has only mic and send; production says "Run was stopped. Results may be incomplete." **[proposal]** `action=stop` with a Regular `circle-stop`. *Refs:* Primer, Fluent, Apple.

**AI10. Put Copy, Retry and Edit on the message; keep feedback optional, quick and specific, and say what is sent.** Controls beside the output get used; vague prompts hide what people agree to share. *GAIDS:* `Chat/Message Actions` (copy, debug) exists but is placed on no screen; Retry and Edit are undrawn. **[proposal]** Regular thumbs-up and thumbs-down `icon-ghost` small buttons that open short reasons and one line on what is included; production uses emoji and hand-made SVGs. *Refs:* Apple, Primer, Carbon, Fluent.

**AI11. Show the `ToolCall/Thinking Line` as soon as a reply or run starts, name the work, animate only live work and stop when it ends; report run state with `RunStatus/Chip`.** Agent runs always outlast the 1 s of U13, and silence reads as failure; motion that outlives work misleads. *GAIDS:* one thinking line per message (`Brand/Gooey Bot` plus shimmer; label priority: running tool, "Summarizing…", "Thinking…"); known length uses `Progress`; a long run uses `RunStatus/Chip` plus email; other waits follow U13. **[gap]** Dark Failed chip text is 4.23:1. Announcements are A12. *Refs:* Fluent, Apple, Primer, Atlassian.

**AI12. Collapse reasoning and tool use into one muted line, expand into labelled rows, and keep raw input behind a link; list sources behind a "Sources" toggle after the answer, each linked to what it supports.** The answer must win; raw payloads can hold private data. *GAIDS:* `Chat/Activity` ("Thought for 2s, 3 tools used", `text/secondary`, one chevron, no emoji) over `ToolCall/Row` (`link` boolean) and `ToolCall/Thought`; `Chat/Sources Toggle` (books glyph, chevron). **[gap]** the Sources toggle is placed on no screen and its open list is undrawn. *Refs:* Atlassian, Fluent, Primer, Carbon, Apple (collapse reasoning and tool use, raw logs behind disclosure); Fluent and Apple (link sources, explain the basis of a result); the Sources toggle itself is GAIDS's own.

**AI13. Offer a few starters and follow-ups, each a complete request the person could type; show what the agent keeps (knowledge files, memory entries) and let people view and delete it; say what a model setting changes beside the control.** Starters teach; hidden memory makes behaviour unexplainable; builders are not model experts. *GAIDS:* three starters in the Ask Gooey splash and Tools empty state; `Copilot/Follow-up Chip`; `Knowledge/Drop Zone` and file rows; "Higher values take more risks" on Creativity. **[gap]** the follow-up chip carries an emoji; no memory-entry screen is drawn. *Refs:* Apple, Fluent, Carbon.

---

## 13. Building and evolving the system

**B1. Treat the published GAIDS library as the source of truth for colour, spacing and radius; code follows it.** One owner of values stops two files drifting. *GAIDS:* file `7wRztN1MVtGDdox6PfctVs`; the superseded Gooey-Design-File gives no values. Describe code as it ships and call Figma names "target" until the migration lands. *Refs:* standing rule; Atlassian, Polaris and Spectrum treat token data as the source and deliver it to Figma and code.

**B2. Use three token tiers and bind only the middle one: primitives hold ramps, semantic roles hold meaning, component roles serve one component.** *GAIDS:* `.Color/Primitives` is hidden with empty scopes; bind `Color/Semantic`; `switch/*` and `run/*` serve their own components. *Refs:* Carbon, Polaris, Spectrum, Primer.

**B3. Name tokens for role as group/role, add a state suffix when needed, and set code syntax to `var(--gooey-<role>)` on every token meant for code, even if code lacks it today.** A role survives a palette change; Dev Mode wraps any string as a custom-property name. *GAIDS:* `text/secondary`, `bg/primary-hover`, never `ink-muted`. **[gap]** code syntax is absent on `space/half`, `radius/tiny`, `radius/compact`, `bg/hover`, `bg/active`, `bg/input`, `bg/primary-hover`, `action/secondary` and `switch/*`; `radius/small`, `regular` and `big` carry the legacy `-xs`, `-sm` and `-md` syntax (Appendix C #12). *Refs:* Carbon, Atlassian, Primer, Spectrum.

**B4. File each component on its level page, in a section named for its family, named `Family/Name`, with a description that starts `Level: Atom`, `Level: Molecule` or `Level: Organism`.** Levels keep the library scannable. *GAIDS:* an atom is one job with no library component inside (icons and brand glyphs aside); a molecule is two or more atoms with one job; an organism is a section with its own layout and slots; code is not renamed for levels. **[gap]** nine components lack the Level line (`Nav/Workspace Row`, `Nav/Account Menu`, `Nav/Learn More Menu`, `Nav/Workspace Switcher`, `Settings/Section`, `Settings/File`, `Settings/Notice`, `Workspace/About Panel`, `Mobile/About Panel`). *Refs:* standing rule (atomic levels); Primer (name layers for what they hold).

**B5. Put a doc frame 80px above every component: name, "Where it's used", code references.** Readers see purpose and production counterpart at a glance. *GAIDS:* the frame is named a single space; `Heading/H2` name, `UI/Strong` heading, `Body/Large` note, `Meta` code references. *Refs:* Primer, Polaris.

**B6. Use a variant when only styling or state changes; make a separate component when function changes. Name axes with one lower-case word and reuse names across sets.** One set per job keeps property panels short. *GAIDS:* axes `state`, `kind`, `size`, `hierarchy`, `tone`; states `default | hover | disabled`, `focus | filled` on inputs, `active` on `Tab`, `pressed` on touch rows; phone versions are separate `Mobile/*` components. Match property type to job: BOOLEAN for an optional part (bind it only where the toggle is a real choice), TEXT for copy, INSTANCE_SWAP for an icon or logo, SLOT for variable content. **[gap]** value casing mixes (`Tag`, `Yes|No`). *Refs:* Primer, Spectrum, Polaris.

**B7. Prefer a native slot to an instance swap or a detached copy; package recurring combinations as molecules.** The atom depends on nothing, and library fixes still flow in. *GAIDS:* `Button` `slot`, `Modal/Dialog` `content`; `Topbar/Eco Cost` is a ghost `Button` plus Eco Readout. **[gap]** `Modal/Dialog` has no header or footer slot. *Refs:* Primer, standing rule.

**B8. Build a component only after the owner approves the design and the pattern repeats; until then draw a stand-in named `[stand-in] Family/Name`, annotated with the missing component and its code file.** Early components freeze guesses; the next builder knows what to replace. *GAIDS:* hold pattern; the note reads "Missing component: Family/Name. File.tsx: spec"; the code is the truth. Look for a new component before standing in. **[proposal]** an entry bar: every property bound, Light, Dark and phone checked, states drawn, doc frame, a `Level:` line and an `A11y:` line (role, name source, keys, focus target, announced state, live politeness, reduced motion). *Refs:* Polaris, Primer; Primer, Spectrum, Fluent and Carbon for accessibility notes in component docs.

**B9. Build screens only from library instances, with content in native slots; never detach.** A detached copy stops receiving fixes. *GAIDS:* `Workspace/Pane` holds a `Workspace/<Tab> Panel` in its `content` slot; a missing part gets a stand-in. *Refs:* Spectrum, Polaris.

**B10. Write each description in a fixed order (Level line, purpose, anatomy, properties, built from, production file, known gaps, date added); fix any sentence a change makes false; hand off through Dev Mode and let developers translate, never add a second token.** Agents read descriptions literally; one name per decision stops duplicates. *GAIDS:* say "DESIGN DECISION" where Figma departs from production, and what production ships for a snapped value; code syntax may name a token code does not ship yet. **[gap]** stale descriptions: `Button` says radius 12 and cites a Legacy/Button that does not exist, `Switch` says 44x24, `Modal/Dialog` says scrim 30%, `Nav/Sidebar Rail` says 64. *Refs:* Primer, Polaris, Carbon, Atlassian.

**B11. Deprecate before you delete: start the description with `DEPRECATED <date>:`, name the replacement, keep it until no instance remains. Before deleting a variable, audit references, repoint, delete, then confirm the file is self-contained.** The published library keeps serving deleted variables, so breakage appears only at the next publish. *GAIDS:* `ToolCall/Card`, `Chat/Reasoning Toggle`, `ToolCall/Group` and `ToolCall/Summary` are deprecated; use the `gooey-figma-tokens` skill. **[gap]** `ToolCall/Card`'s note has no date and points at deprecated parts; it, `ToolCall/Group` and `ToolCall/Summary` have no Playground instances left; live `Chat/Error Bubble` nests a deprecated component; `Composer/Bar` binds the removed `radius/huge`. *Refs:* Polaris, Atlassian, Primer, Spectrum.

**B12. Log every change in `GAIDS_CHANGELOG.md` in the same turn (dated, newest first: what, where, why) and echo decisions into `DESIGN_TOKENS.md`.** The log is the audit trail; the other file is the spec. *GAIDS:* regenerate the colour table from live Figma; new components, tokens and icons stay invisible to other files until the owner republishes; the process for echoing decisions may change when the Discord agents arrive, about 2026-10-09. **[gap]** both files are untracked in git. *Refs:* Primer, standing rule.

**B13. Test each new component and screen in Light, Dark and at phone width, and prove refactors changed nothing visually.** Breakage hides in the view you skipped, and most contrast failures are Dark-only. *GAIDS:* set Dark on a throwaway clone, never on the original frame, with the mode set on `Color/Semantic` and, for WhatsApp, `.Color/WhatsApp`; components never pin a mode; compare a pixel hash or node fingerprint before and after; below 992px layouts are one pane. **[gap]** most Playground states are drawn in Light only (one Dark frame in the components audit, six in the foundations audit); code has no dark block. *Refs:* Polaris, Atlassian, Primer, Carbon.

**B14. Draw an unapproved idea on Playground as real instances, one frame per state; it stays a proposal, with no components and no `DESIGN_TOKENS.md` decision until the owner approves.** *GAIDS:* changelog entries are still written; the model picker, Tools, Settings and Variables are proposals. Add "What changes" and "Still open" headers or other annotations only when the owner asks; otherwise put the same content in the changelog entry. *Refs:* Carbon, Primer, Polaris.

**B15. When a change alters how a component looks, list the options and let the owner choose; never pre-pick the remaining 6px and 2px cases (L2). Edit the shared file defensively.** One accountable owner replaces a review board; others edit concurrently. *GAIDS:* re-list a section before laying out or deleting, remove only nodes you created, ask before downloading anything. Appendix C carries recommendations as a starting point, not a call made. **[proposal]** make library edits on a Figma branch the owner reviews before merging. *Refs:* Primer (branch and review with a named owner), standing rule; Carbon runs a governance board, which GAIDS does not adopt.

---

## 14. Before you ship: checklist

Run this on every screen or component. Each line points at the rule. Lines marked (proposal) rest on rules the owner has not approved yet: check them, but draw a stand-in rather than editing a library component.

**Tokens and structure**
- Does Inspect show a variable or a named style, with no literal, on every fill, stroke, space, radius, text node and effect, with zero bound to `space/0`? (P7, C1, L1, L2, T1, S4)
- Does the screen start from `Shell/App Shell` or `Mobile/Screen` and use library instances in slots, with each gap a `[stand-in]`? (N7, B8, B9)
- Is any bordered card inside another (a `Settings/Section` in a pane is allowed until Appendix C #8), and are records you compare drawn as hairline rows? (N3, N4)
- Does each container hold exactly one primary `Button`, and does it read as ink? (N6, C3)
- Does every nested corner equal its parent's radius minus the padding between them, with no child larger than its parent, and does each shadow sit on a surface that covers other content? (S2, S4)

**Colour and type**
- Does every text and icon pair reach 4.5:1 or 3:1 per Appendix A in Light and Dark, with `text/tertiary` only on `bg/page` or `bg/input`? (A1)
- Does any state rely on colour alone, and does each status colour keep its single meaning? (C6, C7, C10)
- (proposal) Does any panel use more than 16, 14 and 12 (plus 18 for a stat value), and does any literal text size remain? (T1, T5)
- Are numbers right-aligned with a space before every unit, one format per column, estimates labelled? (T10, W8, AI5)

**Behaviour and accessibility**
- (proposal) Can you tab through in visual order, see focus on every stop, and close every overlay with Escape back onto its trigger? (A4 to A7)
- Does every icon-only button have a written name and tooltip? (A10)
- (proposal) Is every interactive element at least 24 by 24 including its hit area? (A9)
- (proposal) Does each animation have a reduced-motion state, and does anything pulse as the only signal? (M1, M3)
- Does the screen survive 200% text, a 320px column, a Hindi string and a string 50% longer? (A13, A17, T12)

**Words and patterns**
- Is every new string sentence case, verb-first on buttons, with no full stop on a label, no exclamation mark, no emoji and "…" for ellipses? (W2, W3, W6)
- Does each error say what happened and what to do next, appear in place, and offer Try again with details collapsed? (W10, U15)
- Does each empty view give its cause and one next action, and does a filtered-to-nothing view name the filters? (U14, U10)
- Is every destructive action a danger row placed last, and does every irreversible action have a confirm that names the object and repeats the verb? (U16, W11)
- Is every mockup string real, and every invented number labelled as invented? (W7)

**AI surfaces**
- Does every message show by container who is speaking, and is the design free of glow, glass, gradients and an AI-only colour? (AI1, AI2)
- Do run-start and model-choice points show cost and CO₂e together, and does every action with real-world effect have a confirmation and a way to stop? (AI5, AI7, AI9)

**Process**
- Was it checked in Light, Dark and at phone width, with the mode set on a throwaway clone? (B13)
- Is there a dated `GAIDS_CHANGELOG.md` entry, plus a `DESIGN_TOKENS.md` line if a decision was made (none for an unapproved proposal)? (B12, B14)

---

## Appendix A. Contrast pairings

From the live WCAG 2.1 audit of 2026-10-06, Light / Dark. Pick colour pairs from these tables, and write the ratio and background beside any colour you add (A1). Text needs 4.5:1; icons and the sole edge of a control need 3:1. **Bold** marks a failure of the 4.5:1 text bar (check the `icon/*` cells against 3:1). Re-measure before quoting; values change when tokens do.

| Ink | `bg/page` | `bg/surface` | `bg/panel` | `bg/selected` | `bg/hover` | Use |
|---|---|---|---|---|---|---|
| `text/primary`, `icon/primary` | 18.80 / 16.70 | 18.15 / 12.42 | 17.40 / 10.39 | 15.34 / 7.45 | 16.34 / **3.04** | titles, body, labels |
| `text/secondary`, `icon/secondary` | 6.84 / 8.15 | 6.60 / 6.06 | 6.33 / 5.07 | 5.58 / **3.64** | 5.94 / **1.48** | supporting copy |
| `text/tertiary`, `icon/tertiary` | 4.57 / 5.79 | **4.42 / 4.31** | **4.23 / 3.60** | **3.73 / 2.58** | **3.98 / 1.05** | meta text only on `bg/page` or `bg/input` (4.61 / 6.50) |
| `icon/muted` | 3.21 / 4.06 | 3.10 / 3.02 | **2.97 / 2.53** | **2.62 / 1.81** | **2.79 / 1.35** | decorative or already-labelled icons |

| Status and brand ink (text, 4.5:1) | `bg/page` | `bg/surface` | `bg/panel` | On its own wash |
|---|---|---|---|---|
| `status/success`, `brand/gooey-teal` | 6.82 / 10.90 | 6.59 / 8.11 | 6.32 / 6.78 | `bg/ok-wash` 6.00 / 8.09 |
| `run/running-ink` | n/a | n/a | n/a | `run/running-bg` 6.48 / 10.55 |
| `status/warning` | 4.89 / 7.97 | 4.72 / 5.93 | 4.52 / 4.96 (thin) | `run/warn-bg` 4.58 (thin) / 6.39 |
| `status/danger` | 6.17 / 4.93 | 5.96 / **3.67** | 5.71 / **3.07** | `run/error-bg` 5.65 / **4.23** |
| `brand/gooey-blue` | 9.64 / 5.87 | 9.31 / **4.37** | 8.92 / **3.66** | n/a |
| `text/primary` on a wash | | | | `bg/ok-wash` 16.52 / 12.40; `run/warn-bg` 17.63 / 13.39; `run/error-bg` 17.23 / 14.33 |

| Other pair | Light / Dark | Use |
|---|---|---|
| `line/soft` on `bg/page` | 1.30 / 1.80 | dividers and containers only |
| `line/default` on `bg/page` | 1.49 / 2.25 | dividers and containers only |
| `line/strong` on `bg/page`, `bg/surface`, `bg/panel` | 3.21, 3.10, **2.97** / **2.72, 2.02, 1.69** | the only candidate edge for a control; passes in Light on page and surface only |
| `action/on-primary` on `action/primary` | 18.80 / 16.70 | primary Button label |
| `text/inverse` on `bg/inverse` | 18.80 / 16.70 | tooltips |
| white `#ffffff` on `bg/info` | 9.71 / 9.71 | the only ink allowed on `bg/info` |
| `text/inverse` or `action/on-primary` on `bg/info` | 9.64 / **1.93** | never; `bg/info` is blue in both modes |

**Also failing or thin.** Switch: `switch/off-bg` against `bg/page` is 1.49 / 2.72 and against `bg/surface` 1.43 / 2.02, the white knob on Dark `switch/on-bg` is 1.12, and on Light `switch/off-bg` it is 1.50. WhatsApp (third party; report, never recolour): `whatsapp/on-brand` on `whatsapp/brand` 1.98 / 1.98, `whatsapp/text-secondary` on `whatsapp/bubble-out` 4.19 / 2.61. Exempt by decision, do not fix: run-chip borders (`run/running-line` 1.47 / 5.11, `run/warn-line` 1.27 / 2.05, `run/error-line` 1.34 / 1.99), because the state is in the text. Thin passes to protect: `text/tertiary` on `bg/page` Light 4.57; `status/warning` on `bg/panel` Light 4.52 and on `run/warn-bg` Light 4.58. In code, the v2 focus colour `#02c4c8` on `#fffefd` is 2.14:1 and the ring sits on `:focus`, not `:focus-visible`.

---

## Appendix B. Known gaps, in suggested priority order

Every **[gap]** is tagged inline; these are the ones with the most effect. None has been changed in the Figma file. Each fix to a library variable, style or component needs the owner's sign-off (Appendix C, B15); re-verify the value before proposing it, because other editors change the file concurrently.

| # | Gap | Rules |
|---|---|---|
| 1 | Dark `bg/hover` is `surface/600` and fails every ink token; it looks like a wrong mapping | C11, A1 |
| 2 | Controls (inputs, checkbox, secondary Button, Tag) are bounded by `line/default`, 1.49 / 2.25:1; `line/strong` in Dark fails too | A2, S3 |
| 3 | No library component has a focus ring that reaches 3:1 (the Slider's hover and focus halo is 15%); code has 11 `outline: none` against 7 `:focus-visible` | A4 |
| 4 | Dark `status/danger` and `brand/gooey-blue` fail as text on `bg/surface` and `bg/panel`; `text/tertiary` fails off `bg/page` and `bg/input` | A1, A3 |
| 5 | Interactive pieces under 24 px: small icon Buttons, Switch, Checkbox, Slider thumb, three chat components | A9 |
| 6 | No input error state, confirm dialog, Stop control, shared Empty State, Skeleton or Spinner; `Modal/Dialog` has no header or footer slot | A14, U13, U14, AI7, AI9, N7 |
| 7 | Dangling bindings: `radius/huge` (deleted) on `Composer/Bar` WhatsApp, deleted primitives on `Brand/Builder Logo` | S1, B11 |
| 8 | Literal colours in components (`#3b404d`, `#82858d`, `#21d562`, five `#ffffff` slot fills) and literal text (secondary Button label, Avatar initials, Home titles, about 1,350 mono nodes) | C1, T1 |
| 9 | Housekeeping: `bg/info` is unused and fails Dark; eight tokens are missing from `DESIGN_TOKENS.md` (`action/secondary`, `bg/active`, `bg/input`, `switch/*`); several lack code syntax; nine components lack the Level line | C15, B3, B4 |
| 10 | `Code` text style points at Menlo, which cannot load; no mono 12 style; no Devanagari fallback | T11, T12 |
| 11 | Control heights drift (small Button 20 to 28 by kind; inputs 39 and 50; code 40) and `Composer/Bar` radius 20 is not concentric | L8, S2 |
| 12 | Static shadows on `Workspace/Pane`, `Shell/App Shell` and `RunStatus/Chip`; black shadows are not mode-aware in Dark; `Elevation/2` and all values are unwritten | N2, S4, S6 |
| 13 | Motion has no spec; `popOut`, `fadeInBackground`, `spin` and others ignore reduced motion; the app has no `aria-live` | M2, M3, A12 |
| 14 | A deprecated component sits inside a live one (`Chat/Error Bubble` nests `Chat/Reasoning Toggle`); stale descriptions (`Button`, `Switch`, `Modal/Dialog`, `Nav/Sidebar Rail`, `bg/selected`, `run/running-ink`) | B10, B11 |
| 15 | Most states are drawn in Light only | B13, A1 |
| 16 | Code is not migrated: pigment token names, no dark block, radius steps differ, scrim 30% against 50% / 75%, about a quarter of spacing values bound, emoji in 66 Python files, legacy "Please" and "Doh!" copy, 19 raw z-index values from 1 to 1,000,000 (the Eco modal's 1080 sits over Bootstrap's modal at 1055; name a ladder that mirrors S7) | B1, L1, S8, I7, W1 |
| 17 | `DESIGN_TOKENS.md` and `GAIDS_CHANGELOG.md` are untracked in git | B12 |

---

## Appendix C. Decisions for the owner

Each decision changes how something looks or works, so it is yours to take. The recommendation is a starting point, not a call made; until you decide, the rules stand as written.

| # | Decision | Options | Recommendation | Rules |
|---|---|---|---|---|
| 1 | Dark `bg/hover` | repoint to `surface/800`; or drop it and use `bg/panel` | repoint now, review dropping later | C11 |
| 2 | Control edges | keep `line/default`; or rest on `line/strong` and lift Dark `line/strong` to `neutral/500`; or add a 3:1 border token | rest on `line/strong`, lift Dark `line/strong`, and decide with #3 what marks hover and focus instead (a new token breaks the 5% rule) | A2, S3 |
| 3 | Focus ring | `brand/gooey-blue`; `action/primary`; teal | new `focus/ring` aliasing `brand/gooey-blue`, 2px, 2px offset | A4 |
| 4 | Dark danger and brand-blue text | `coral/400` or `coral/300`; `blue/400` only if used as text | `coral/400`; no danger text on `bg/panel` | A3 |
| 5 | `bg/info` | delete after the reference audit; or keep with fixed white ink | delete | C9 |
| 6 | Disabled treatment | one opacity everywhere; or disabled tokens | one opacity, 0.5 | A15 |
| 7 | WCAG level and hit area | stay at 2.1 AA; or add target size 24, focus not obscured and dragging alternatives | 2.1 AA plus those three; 24px floor, Button stays 36 | A9, A6 |
| 8 | Is `Workspace/Pane` a card or a frame? | frame (one card level inside is fine); or card, with hairline sections | frame | N3 |
| 9 | Home collections | four card grids; or rows for Recent and Saved, cards for Industry and News | the split | N4 |
| 10 | Shadows and Dark elevation | keep static shadows and document `Elevation/*` (this rewrites N2 and S4 to sanction them); or flatten; for Dark add a hairline to dialog and sheet (an edit to S6 and S8) or a mode-aware shadow | document as drawn, add the hairline when Dark ships | N2, S4, S6 |
| 11 | Control height ladder | 28 / 36 / 40; or 28 / 36 | 28 / 36 / 40; move `Input/Control` 50 to 40, others to 36 one at a time | L8 |
| 12 | Radius names and odd values | Figma names into code; or code names into Figma; card, chip, Composer, sheet and Eco-dialog radii | adopt Figma names in code; 12 for containers that group controls, 16 for object cards, `radius/small` for chips; keep 16 and add no token for sheets and dialogs | S1, S2, L3, B3 |
| 13 | Save model | autosave with a "Saved" status; or one explicit Save with the unsaved dot on desktop | one explicit Save (phone already works this way) | U6 |
| 14 | Toast, danger Button, Completed chip | none / none / no chip; or add them | none for all three until a drawn case needs one | U11, U16, U12 |
| 15 | Components to build next | Empty State, Skeleton row, Spinner, confirm dialog, Stop action, Dialog header and footer slots | build all before drawing more screens | U13, U14, AI7, AI9, N7 |
| 16 | The `sparkles` glyph | only on actions that start generation; or everywhere; or retire it | retire it from "Best match" and thought rows, as PRODUCT.md names sparkles; decide Ask Gooey separately | I10, AI2 |
| 17 | AI-written content, limits line, feedback, "Thinking" | `Meta` "Generated" line; limits once in the empty state; thumbs plus reasons on live runs, none in Preview; keep "Thinking" | adopt all four | AI3, AI10 |
| 18 | Mono face and missing styles | Menlo; Geist Mono; system stack | Geist Mono for `Code` at 14 plus one 12 mono style | T11 |
| 19 | Body size and heading weight | 14 or 16 base; Medium or Semi Bold headings | 14 for panels and dialogs, `Body/Large` for fields and reading; keep headings as drawn and fix code | T3 |
| 20 | Non-Latin and RTL | system fallback; Noto Sans after Inter; a Devanagari companion font | Noto Sans after Inter plus a Hindi test frame; RTL out of scope for v1 | T12, A17 |
| 21 | Vocabulary | money words (dollars, credits, funds, "Cr"); agent vs workflow vs app; Sign in vs Login | dollars wherever an amount shows; "Agent Builder" for the editor, "agent" and "workflow"; "Sign in" | W4 |
| 22 | Sentence case and overlines | confirm sentence case for all new copy; retire the uppercase overline | both | W2 |
| 23 | Cost icon and avatar shape | `circle-dollar` for price and `coin` for balance; circle for a person and Rounded for an agent | both | I6, I9 |
| 24 | Motion tokens | adopt three durations and two curves in code first, record after approval | as described, no Figma variables yet | M2 |
| 25 | Principles P6 to P8 | adopt all, some or none | P6 yes; P7 and P8 only if you want them at principle level (B-section and section 9 already carry them) | section 1 |
| 26 | Process | Figma branches for library edits; deprecation runway; stand-in annotation; entry threshold; commit the two spec files; Code Connect and lint | branches yes; no instances left plus one publish cycle; Figma-native annotation on stand-ins only; second screen plus owner approval; commit; defer Code Connect and lint until tokens are renamed | B8, B11, B12, B15 |

---

## Appendix D. Reference systems and where GAIDS differs

**What each reference mainly contributed.** The full digests are in `design-systems/`.

| System | Mainly used for |
|---|---|
| Apple HIG | accessibility, writing, motion restraint, generative AI and permission patterns |
| Material 3 | adaptive layout, colour roles and contrast, accessibility, motion |
| Fluent 2 | content design, loading and feedback, AI and Copilot guidance, tokens |
| Carbon | patterns (forms, status, empty states), accessibility, Carbon for AI, content |
| Atlassian | tokens and elevation, motion durations, voice and tone, patterns, governance |
| Polaris | content, patterns, agent guidance, error and empty states, deprecation stages |
| Primer | UI patterns, accessibility, agent patterns, contribution path |
| Spectrum | attention hierarchy, colour and contrast, density, a word list for generative features (no AI guidance as such) |
| Stripe | precise data presentation, colour-system method, filters and tables, Apps patterns |
| Astryx (existing file) | composition: nesting, adjacency, region budgets |

**Standing decisions where GAIDS departs from the references.**
- **Success is teal, not green;** the primary action is ink, not a brand colour; information is neutral (no `status/info`). Most references use green, a brand-coloured primary and blue for info.
- **Opaque tints, not alpha:** Atlassian, Fluent and Carbon ship alpha tokens; Figma drops opacity on variable-bound paints.
- **Weight and ink at one size:** Apple, Atlassian, Polaris, Spectrum and Primer also rank with size steps; GAIDS reserves size steps for headings and stat values.
- **One breakpoint (992px) and no column grid,** against Astryx 1024 / 768, Material width classes, Primer 768, Polaris 768 / 1040, and Atlassian's 12 and Carbon's 16 columns; a 4px unit, where Carbon and Atlassian use an 8px base with 2px and 4px steps below it, Material uses 8, Spectrum a geometric ramp, and Fluent and Polaris 4.
- **36px Buttons and no 44px rule,** where Apple, Spectrum, Polaris, Fluent, Carbon and Material say 44 to 48; GAIDS recommends only a 24px floor.
- **No glass, blur or gradient materials** (Apple, Fluent, Spectrum) and no AI colour, glow or generative border (Carbon's aura and gradient border, Atlassian's Rovo colours, Polaris's purple "magic" role, Fluent's Copilot shimmer).
- **Regular icons first, no emoji, `Family/Name` component names;** Primer's PascalCase names and "?" booleans, and release phases, semver and codemods (Carbon, Atlassian, Polaris, Primer), are not adopted.

**Current practice the owner has not yet decided (Appendix C).**
- **No toast** (Fluent, Atlassian, Carbon ship one; Primer argues against) and **no danger Button** (Carbon, Stripe, Polaris, Spectrum, Primer and Apple's destructive role have one): #14.
- **Sentence case for new copy** (Apple uses title case for buttons and menu items): #22.
- **Once-only AI limits line** instead of Fluent's per-reply disclaimer, and the **"Thinking" disclosure** despite Fluent's caution against verbs like "thinks": #17.
- **Opacity for disabled controls** (Polaris says never): #6.

---

## Appendix E. Not yet covered

Topics at least two references cover that matter to Gooey but that these guidelines do not yet address, because the facts are not recorded or the owner has not decided. Ask for a rule when one of them comes up.

| Topic | Why it matters here | Open question |
|---|---|---|
| Roles and permissions | one agent page serves owners, editors, visitors and members | hide a control the role can never have, or show it with the reason? (A15 says explain) |
| Connecting accounts, API keys and secrets | the Integrations dialog and API page give agents real-world reach; account connection is undrawn | mask saved secrets, explicit Save for secret fields, never show a secret twice |
| Inspecting a past run | builders learn by watching an agent fail and fixing it; Debug and Usage tabs are undrawn | one fixed order for steps, inputs, outputs, cost and error, behind one link |
| Run finished while away | runs take minutes; code already offers an email | opt-in only; show on the History row, never a count badge |
| Charts and data visualisation | Usage, Eco tiles and Total Turns are the likely first charts | when to chart, zero baselines, a table equivalent; no chart component or token exists |
| Tables and long lists | a compare table is drawn as a plain frame; code pages History with "Load more" | sorting, row actions, bulk selection, column units |
| Writing tool names and descriptions | the model reads them as well as the builder | verb first, what it does, when to use it, whether it changes anything outside Gooey |
| Version history and restore | Publish suggests versions; nothing is specified | does Publish create a restorable version with a note? |
| Light or dark by choice | code has no theme mechanism | follow the system setting by default? where does the choice live? higher-contrast support? |
| Shareable state | tab, filters and run id may or may not be in the URL | does state survive crossing 992px? |
| Keyboard shortcuts | only Enter, Shift+Enter and Escape exist | is a command palette wanted? |
| Code and prompt editor | the main authoring surface has only the mono-face rule (T11) | syntax colours literal, 4.5:1 on the editor ground in both modes, error shown by icon plus text, a visible focus ring |
