# SOP: Build a Reusable Shopify Product Detail Page

**Author:** Nicolas Cartin Reyes, Lead Developer

## Objective

This procedure replaces product-specific Liquid templates with one reusable product detail page driven by Shopify product data, typed metafields and collections.

## 1. Audit the existing theme

Identify the production product template, cart form, gallery, review provider, financing integration, product cards, global layout classes and responsive breakpoints. Reuse working components instead of recreating a disconnected visual system.

Create a dependency map before writing code. Separate product-specific data from shared brand content and theme infrastructure.

## 2. Define the data contract

Use Shopify's standard product object for title, description, variants, price, compare-at price, availability, collections and media.[1]

Use typed metafields only for data that does not have a suitable standard product field. Access modern metafields through `.value`. Product-reference lists return iterable product objects in Liquid.[2]

A practical contract can include:

| Need | Recommended source |
| --- | --- |
| Optional membership or service products | List of product references |
| Preferred related family | Collection reference |
| Optional editorial modules | Metaobject reference |
| Product-specific media | File or media reference |
| Finance term | Integer |
| Alternate versions | List of product references |

## 3. Design conditional rendering

Each optional section needs a strict predicate. A video feature should render only when valid video media exists. A press section should render only when quotes exist. A specification image should not fall back to the product's featured image unless that behavior is explicitly part of the data contract.

Shared content can remain fixed when it is genuinely universal. Product-specific content must never use an unrelated generic fallback.

## 4. Build reusable components

Create small snippets for media, product cards, membership options and financing. Keep collection loops and product-reference loops outside the markup-heavy card snippet.

Use native Shopify forms and normal cart endpoints. Preserve the host theme's cart events and third-party discount compatibility.

## 5. Implement collection-aware recommendations

Use the current product's canonical family collection to control the related heading, feed and collection link. If a preferred collection metafield exists, validate that the product actually belongs to it before using it.

Exclude the current product, unavailable products and duplicate IDs. Set an explicit card limit.

## 6. Implement variant synchronization

Variant changes should update the selected variant ID, product price, compare-at state, availability, financing amount and featured media. Use vanilla JavaScript and dispatch a stable custom event for other components.

Do not calculate promotional discounts in the template when a store app owns discount rules.

## 7. Scope styling

Reuse global theme primitives first. Scope every new rule under a stable PDP root attribute. Test long prices, compare-at prices, badges and translated copy. Do not solve overflow by applying `overflow-x: hidden` to the entire page.

## 8. Validate and release

Run syntax checks, Theme Check and targeted hardcode searches. Deploy to an unpublished theme using an explicit `--only` allowlist and `--nodelete`. Pull the remote files after deployment and compare hashes.[3]

Complete desktop, tablet and mobile visual QA before production. Back up the live versions of the allowlisted files and the layout hash. Push only the approved files to the live theme and repeat smoke testing.

## References

[1]: https://shopify.dev/docs/api/liquid/objects/product "Shopify Liquid product object"
[2]: https://shopify.dev/docs/api/liquid/objects/metafield "Shopify Liquid metafield object"
[3]: https://shopify.dev/docs/api/shopify-cli/theme "Shopify CLI Theme commands"
