# Dynamic PDP QA and Release Guide

**Author:** Nicolas Cartin Reyes, Lead Developer

## Static validation

Run JavaScript syntax checks and Shopify Theme Check before uploading. Theme Check analyzes Liquid theme code and theme best practices.[1]

```bash
node --check path/to/pdp.js
shopify theme check --path /absolute/path/to/complete-theme --fail-level error
```

Search for product IDs, variant IDs, product handles, credentials, debug output and unrelated brand assets.

## Draft validation

Deploy only the feature files to one unpublished duplicate. Use an allowlist and `--nodelete`. Pull the same files back and compare them with the local source.

Test at 390, 433, 768, 1000, 1001 and 1280 pixels when a design changes at a 1000-pixel breakpoint. Inspect actual text bounds, not only parent container bounds, when checking price collisions.

## Functional checks

Verify product variants, gallery media, compare-at pricing, stock state, membership or service choices, financing, modal behavior, collection-backed cards, review widgets and optional-section gating.

Do not advance to checkout during routine theme QA. Inspect the cart payload or use a reversible cart test only when necessary.

## Production release

Before production:

1. Confirm the live theme ID and draft theme ID.
2. Back up the live versions of every allowlisted file.
3. Record the hash of `layout/theme.liquid`.
4. Confirm the approved source matches the draft.
5. Push only the allowlisted files to the live theme.
6. Pull them back and compare hashes.
7. Confirm the layout hash did not change.
8. Run public desktop and mobile smoke tests.

## Rollback

Rollback uses the same narrow allowlist. Restore only the backed-up feature files. Never repair a feature deployment by pushing a complete theme unless the complete theme itself was the approved release payload.

## References

[1]: https://shopify.dev/docs/api/shopify-cli/theme "Shopify CLI Theme commands"
