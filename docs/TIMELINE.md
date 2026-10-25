# Connected timeline

`scripts/timeline.js` joins authors and the existing saints guide by `author_id`. It does not maintain another saints dataset. `#/timeline/saints` opens the saints filter; `#/timeline/person/<id>` opens a person from their author page. Saints pages link back to the timeline.

Search includes names, aliases, writings, and biographies. Filters cover saints-guide entries, authors, Doctors, century, and editions readable here. Every recorded status stays explicit.

Authors retain their principal-work century. Additional people use death year, then birth year. Archangels, undated figures, and figures marked primarily traditional remain outside the dated sequence. Historical flags and sources remain visible.

Writings by a person and lives about them use separate explicit data relationships. Read-here buttons require a rights-checked hostable edition; missing rights data fails closed. Raw Isidore links are excluded. Profiles retain the complete source lists.

The static timeline has crawlable profile and selected-work links. Run the normal build and static generator after changing the template. `tests/timeline.test.js` checks joins, filters, chronology, and rights gates.
