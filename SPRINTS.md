# Sprints
## Sprint 1 — Local working MVP
- [x] Create independent public GitHub repository
- [x] Build accessible, responsive editorial website with Scroll Craft
- [x] Write three sample journal articles with working navigation
- [x] Implement working contact and pending subscription storage
- [x] Supply Docker Compose and persistent database
- [x] Add CI and server integration tests
- [x] Complete desktop/mobile/reduced-motion headless browser verification across scroll positions
- [x] Verify running Docker container, health check, and form submissions; LAN port 8099 (requires network allowlisting)
## Sprint 2 — Production readiness
- [x] Resolve port conflict with Workbench3D by using 8099
- [x] Fix automated WCAG 2.0/2.1 A/AA color-contrast failures
- [x] Add repeatable browser and accessibility checks to CI
- [x] Add local operator CLI for viewing, exporting and unsubscribing leads
- [ ] Set up custom domain, TLS and chosen hosting
- [x] Add optional encrypted SMTP contact notification support with no provider enabled by default
- [ ] Configure and validate an authorized mailbox; add consent-based newsletter provider
- [ ] Confirm company contact/legal details and review privacy/retention practices
- [ ] Add SEO schema, sitemap, canonical and search indexing checks
- [ ] Add privacy-safe visitor analytics after consent policy review
## Sprint 3 — Commercial experience
- [x] Refine editorial grammar: hard-cut belief scene and non-card service list
- [ ] Implement consultation intake and scheduling workflow
- [ ] Add genuine case studies, proof points and customer outcomes
- [ ] Add a manageable blog publishing process and content calendar

## Sprint 4 — Temporary public preview
- [x] Add static GitHub Pages build with correct project URL paths
- [x] Disable backend-dependent contact and newsletter forms on Pages
- [x] Keep local full-stack Docker environment unchanged
- [x] Add GitHub Actions Pages workflow with static link and browser tests
- [ ] Verify Pages deployment and public URL responds after workflow merge
- [ ] Connect secure production backend and mailing workflow before public form activation
