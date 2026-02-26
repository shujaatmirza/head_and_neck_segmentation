Generate a polished, self-contained HTML slide presentation from the provided content.

## Input

The user will provide one of:
- A file path to a paper, report, or document (PDF, TeX, markdown, etc.)
- Raw text/content to summarize into slides
- A topic and key points

The argument is: $ARGUMENTS

## Output Requirements

Create a **single self-contained HTML file** (no external dependencies except Google Fonts) with:

### Design
- Dark theme with CSS custom properties (deep navy/charcoal background, cyan/purple/amber accents)
- Modern sans-serif font (Space Grotesk) + monospace for data (JetBrains Mono)
- Responsive layout using clamp() for all sizes
- Subtle gradient backgrounds per slide type (title, section, content, results, conclusion)
- Smooth slide transitions with CSS transforms and opacity
- Staggered fade-in animations for child elements

### Slide Types & Components
- **Title slide**: project name, subtitle, divider, description
- **Section slides**: large decorative section numbers, tags, cards
- **Content slides**: two-column layouts, feature lists, tables, bar charts
- **Results slides**: animated horizontal bar charts with data-width attributes, insight callouts
- **Conclusion slide**: bold summary statement with key metric highlighted

### Interactive Features
- Keyboard navigation (arrow keys, space, home/end)
- Touch/swipe support for mobile
- Click navigation (left/right halves of screen)
- Bottom progress bar showing current position
- Animated bar charts that fill when slide becomes active

### Structure
- 10-15 slides covering: title, problem/motivation, data, methods, results (multiple), key insights, limitations, conclusion
- Each slide has a slide number indicator (e.g., "03 / 13")
- Use cards, grids, bar charts, and tables to present data visually
- Include "insight" callout boxes for key takeaways

### Code Organization
- All CSS in a single `<style>` block in `<head>`
- All JS in a single `<script>` block before `</body>`
- No external files or dependencies (except font import)

## Process

1. Read the source content if a file path is provided
2. Extract the key information, data, and findings
3. Organize into a logical slide narrative
4. Generate the HTML file and save it alongside the source (or in the current directory)
5. Tell the user how to view it (open locally, or use htmlpreview.github.io for GitHub)
