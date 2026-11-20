# Repository and Deployment Safety

**Author:** Nicolas Cartin Reyes, Lead Developer

## Public repository boundary

This repository must not contain store access tokens, Theme Access passwords, API keys, customer data, internal theme IDs, unpublished assets or proprietary storefront source.

Examples must use generic metafield names and placeholder identifiers. Screenshots from private storefronts require explicit approval before publication.

## Credential handling

Use authenticated local tooling or environment variables. Never commit `.env` files, CLI session files or command output that includes tokens. Rotate a credential immediately if it is exposed.

## Theme deployment boundary

Use explicit theme IDs and file allowlists. Verify the target theme role before a push. Use `--nodelete` for feature-level changes. Record a baseline layout hash and confirm it after deployment.

A change to layout, checkout, global navigation or a third-party app integration should be reviewed independently from a product-template change.

## References

[1]: https://shopify.dev/docs/api/shopify-cli/theme "Shopify CLI Theme commands"
