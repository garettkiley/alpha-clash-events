# alpha-clash-events

Hourly mirror of every public Alpha Clash event on [XP Network](https://xpnetwork.com/search/events?query=alpha+clash), served as static JSON for the alphaclashtcg.com Events calendar.

**Feed:** https://garettkiley.github.io/alpha-clash-events/events.json (GitHub Pages sends `Access-Control-Allow-Origin: *`, so any site can `fetch()` it).

**How:** `.github/workflows/refresh.yml` runs `fetch.py` at minute 17 every hour. It queries `api.xpnetwork.com/search/events` by game (activity) ID: `activities=6` (Alpha Clash), `394` (Cosmic Conquest) and `395` (Siege of the Forgotten). It unions that with the text query `alpha clash`, paginates with `limit=30` (the API max) and `offset`, de-duplicates by event ID, and drops private, unpublished and test events. `events.json` is committed only when the events change.
