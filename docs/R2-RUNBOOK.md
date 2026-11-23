# R2 runbook

How to upload, verify, roll back, and check usage for the `bibliotheca-files` R2 bucket, served at
https://files.bibliothecacatholica.com. The inventory is [R2-INVENTORY](R2-INVENTORY.md) (generated from
`data/r2-manifest.json`); the migration plan is [plans/r2-migration-plan.md](plans/r2-migration-plan.md).

## Rules

- **Owner approval per batch.** Upload only a batch the owner has approved in writing. Items with `ownerReview` (non-renewal
  scans not yet approved for hosting) are in no batch and cannot be uploaded.
- **Rights first.** An item is listed only with a recorded basis: public domain in the US by date (`tools/rights_rule.py`) or a
  recorded non-renewal check. Unknown rights stay out (`excluded`). Hosting a scan is hosting: the same rules as a text.
- **Immutable keys.** `pdf/<slug>.pdf`, `epub/<slug>.epub` (the EPUB slug keeps its content hash), and `scans/<slug>/...`
  are served with `Cache-Control: public, max-age=31536000, immutable`. A key never gets new content: a corrected scan or
  edition gets a new slug (`-r2`), as corrections to live texts do.
- **No other Cloudflare changes.** No DNS, Pages project, or custom-domain change belongs in an upload. Never print the token.
- **Free tier.** The tool refuses a batch that would take the bucket past 10 GB.

## Upload a batch

1. Refresh the inventory if the catalogue changed: `python3 tools/r2_inventory.py` (offline). `--refresh` re-reads the
   Internet Archive file lists (network: archive.org).
2. Dry run (the default; nothing is uploaded):

   ```bash
   python3 tools/r2_upload.py --batch batch-1
   ```

3. Downloads come from the Internet Archive's file servers (`servers` in each manifest item, for example `ia801903.us.archive.org`).
   In the cloud environment, each server must be on the allowed-hosts list first: ask the owner, never widen it yourself.
4. Upload, once the owner has approved the batch:

   ```bash
   CLOUDFLARE_API_TOKEN=proxy-injected python3 tools/r2_upload.py --batch batch-1 --apply
   ```

   In the cloud environment the network proxy injects the real token for api.cloudflare.com, so the variable holds a placeholder.
   Elsewhere, set it to a token with R2 Storage Edit. The account ID is read from `CLOUDFLARE_ACCOUNT_ID` or asked of the API;
   it is never committed (a test fails if it appears in the repository). Each file is read (or downloaded and checked against the source SHA-1),
   PUT with its Content-Type and cache header, read back, and checked (SHA-256, size, Content-Type, Cache-Control). Its `upload`
   record is written into the manifest as soon as it verifies.
5. Commit `data/r2-manifest.json` with `python3 tools/r2_inventory.py` rerun (the doc shows the batch as uploaded), in a PR.

The first real upload also confirms that the Cloudflare API keeps the `Cache-Control` header on the object. If verification
reports a different cache header, stop, delete the object (below), and report it: the S3-compatible endpoint with an R2 access
key pair is the fallback, and needs the owner to provide the key pair as a network secret.

## Verify

- `r2_upload.py` verifies every object right after its upload. To re-check later, run the batch again: verified objects are skipped,
  so a second run uploads nothing.
- Spot-check the public URL in a browser: `https://files.bibliothecacatholica.com/pdf/<slug>.pdf` should open with
  `content-type: application/pdf` and the immutable cache header.

## Roll back

1. Delete the object and clear its record:

   ```bash
   CLOUDFLARE_API_TOKEN=proxy-injected python3 tools/r2_upload.py --delete pdf/<slug>.pdf --apply
   ```

   Without `--apply` it is a dry run.
2. Revert the manifest change (or commit the cleared record) and any site change that linked to the key. The site shows a file
   link only when the manifest records a verified upload, so a cleared record removes the link at the next build.

## Check usage

```bash
CLOUDFLARE_API_TOKEN=proxy-injected python3 tools/r2_upload.py --usage
```

prints the object count and stored size against the 10 GB free tier (read only). The Cloudflare dashboard shows the same under
R2, `bibliotheca-files`, Metrics. Class A (writes) and Class B (reads) operations also have monthly free allowances; one batch
uses about two operations per file.
