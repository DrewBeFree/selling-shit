# Selling Shit

Marketplace listing draft dashboard for turning item photos and rough notes into platform-specific drafts for Nextdoor, eBay, and Facebook Marketplace.

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app:app --debug run --host=127.0.0.1 --port=5001
```

Open `http://127.0.0.1:5001/`.

If you are SSH'd into Atlas and need a browser-reachable dev URL over Tailscale:

```bash
python -m flask --app app:app --debug run --host=100.71.165.80 --port=5001
```

Open `http://100.71.165.80:5001/` from a device connected to the same Tailscale network.

## Listing Metadata Controls

Each dashboard item card has an editable metadata form for:

- Status: drafting, ready, listed, sold
- Sold price
- Notes
- Watch count
- Response count
- Deadline
- Listing type: fixed price or auction
- Auction end date/time

Click **Save metadata** on the item card to persist the values to the local JSON catalog.

## Catalog Intake

- Drop item folders into `catalogue/inbox/`, then use **Scan catalogue**.
- Scanned and uploaded items live in `catalogue/active/`.
- Archived item folders move to `catalogue/archive/`.
- Each folder can contain photos plus an optional `description.txt`.
- Uploaded photos, scanned item media, and JSON catalog data stay local and are ignored by Git.

## Atlas Deployment

The production service runs as a user-level systemd service on Atlas:

```bash
cp deploy/selling-shit.service ~/.config/systemd/user/selling-shit.service
systemctl --user daemon-reload
systemctl --user enable --now selling-shit.service
```

The service runs Gunicorn on `127.0.0.1:5055`. The intended public hostname is:

```text
sell.drewbefree.com -> 188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com
```

That hostname should be a proxied Cloudflare CNAME/Tunnel record in the `drewbefree.com` zone and should be covered by the Drew-only Cloudflare Access application before public use.
