# Loop Market

Small French music-accessory ecommerce demo built with HTML, CSS and JavaScript with AI assistance. Six fictional products, illustrative MAD prices, generated visuals, search, category/budget filters, sorting, favorites, product dialogs, cart and a simulated summary.

No account, payment, checkout service or order transmission. Simulated delivery costs 25 DH below a 500 DH product subtotal and zero thereafter. Stock limits are illustrative. Cart and favorites are saved only in this browser under `loop-market.v1`; storage failures keep the session in memory. No personal customer information is requested.

Run `node tools/verify_loop_market.cjs` from the repository root to check the catalog and cart calculations. Serve the repository with an HTTP server to test the interface.

Product images were created using imagegen in generation mode, then resized to 900px JPEG for the web. Common prompt: square unbranded single-product commercial photograph, fully visible centered three-quarter view, pure white seamless background, soft diffuse lighting, realistic subtle shadow, no text, labels, logos, prices or watermark. Subjects: ivory over-ear headphones; orange textile portable speaker; charcoal tabletop microphone; white compact MIDI-style keyboard; blue wired earphones; pale-oak headphone stand with charcoal base. Images live in `images/`. They illustrate fictional products and do not establish technical specifications.
