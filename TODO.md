# TODO

## Bugs to fix
- [ ] PDF viewer breaks on some PDFs with weird encoding
- [ ] Groq rate limiting is annoying — maybe add a queue system?
- [ ] The heuristic analysis is pretty garbage for papers that don't follow standard structure
- [ ] Search sometimes returns weird results when papers have lots of tables

## Features I want to add
- [ ] OCR for scanned PDFs (this is gonna be hard)
- [ ] Browser extension to import papers directly from arXiv
- [ ] Better visualizations — the word cloud is kinda basic
- [ ] Share collections with other users
- [ ] Custom analysis templates (like for systematic reviews vs regular papers)
- [ ] Mobile app? (probably not gonna happen lol)

## Code quality
- [ ] The frontend needs better error handling — lots of silent failures
- [ ] Some components are getting too big (looking at you, App.tsx)
- [ ] Should add more tests but honestly I hate writing tests
- [ ] The CSS is a mess in some places — too many !important flags

## Maybe someday
- [ ] Real time collaboration (would need websockets)
- [ ] AI-powered paper recommendations based on reading history
- [ ] Integration with reference managers like Zotero
- [ ] Support for other document types (Word, LaTeX)

## Notes to self
- The LLM integration is the weakest part — need to figure out better prompting
- Supabase free tier has 500MB limit — might need to upgrade eventually
- Render cold starts are killing me — consider moving to Railway
- The collections feature was added last minute and it shows
