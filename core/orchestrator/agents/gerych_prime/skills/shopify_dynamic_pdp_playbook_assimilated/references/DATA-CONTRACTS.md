# Dynamic PDP Data Contracts

**Author:** Nicolas Cartin Reyes, Lead Developer

## Standard Shopify fields first

A reusable product page should use the Shopify `product` object before introducing metafields. The object already exposes variants, media, collections, availability, price and compare-at price.[1]

## Suggested metafields

The following names are examples. Store-specific namespaces and governance should be defined before implementation.

| Example key | Type | Purpose |
| --- | --- | --- |
| `custom.membership_products` | List of product references | Optional service or membership products |
| `custom.parent_collection` | Collection reference | Preferred related-product family |
| `custom.content_profile` | Metaobject reference | Optional editorial modules |
| `custom.finance_months` | Integer | Finance calculation divisor |
| `custom.product_versions` | List of product references | Alternate product/version links |
| `custom.specification_media` | File reference | Optional specification image |

Modern Liquid metafields provide a `type` and a typed `.value`. Lists can be iterated directly.[2]

## Validation rules

A referenced product must have a valid selected or first available variant before it can become a selectable commerce option. A referenced collection should be verified against `product.collections` when it controls category-sensitive recommendations.

A content module should have a stable key and explicit media requirements. A module that requires video should not render from an image-only fallback.

## Collection precedence

A safe related-product algorithm is:

1. Read the preferred collection reference.
2. Confirm that the current product belongs to it.
3. Otherwise use the first appropriate assigned storefront collection.
4. Exclude the current product and unavailable products.
5. Stop at the configured card limit.

This prevents products from one family appearing in another family's recommendation section.

## Commerce ownership

Product and membership variants own their prices and availability. Discount applications own discount logic. The Liquid template should format current commerce data, not reproduce app rules.

## References

[1]: https://shopify.dev/docs/api/liquid/objects/product "Shopify Liquid product object"
[2]: https://shopify.dev/docs/api/liquid/objects/metafield "Shopify Liquid metafield object"
