# Flask Cipher Pages Design

## Goal

Extend the current Flask lab project so the existing Caesar page pattern is also available for Playfair, Rail Fence, Transposition, and Vigenere ciphers.

The new pages must:

- live under `templates/`
- use Bootstrap 4.6.2
- render results on the same page after form submit
- preserve submitted values through Jinja2 variables
- avoid JavaScript
- keep the current Caesar routes working unchanged

## Current Context

The project already has:

- `app.py` with working `GET /caesar`, `POST /caesar/encrypt`, and `POST /caesar/decrypt`
- `templates/caesar.html` using two POST forms and `render_template` to display results inline
- cipher packages for `playfair`, `railfence`, `transposition`, and `vigenere`

Verified class and method names:

- `PlayFairCipher.create_playfair_matrix(key)`
- `PlayFairCipher.playfair_encrypt(plain_text, matrix)`
- `PlayFairCipher.playfair_decrypt(cipher_text, matrix)`
- `RailFenceCipher.rail_fence_encrypt(plain_text, key)`
- `RailFenceCipher.rail_fence_decrypt(cipher_text, key)`
- `TranspositionCipher.encrypt(plain_text, key)`
- `TranspositionCipher.decrypt(cipher_text, key)`
- `VigenereCipher.vigenere_encrypt(plain_text, key)`
- `VigenereCipher.vigenere_decrypt(cipher_text, key)`

## Chosen Approach

Use explicit routes and one template per cipher page, following the existing Caesar implementation style as closely as possible.

Why this approach:

- lowest risk to the current lab project
- easiest to read and demo
- matches the existing Caesar page pattern
- avoids introducing shared abstractions that are unnecessary for a small assignment

Alternatives considered but rejected:

- one generic reusable template for all ciphers: less duplication, but more abstraction than this project needs
- helper-heavy route consolidation: smaller Python surface, but reduced clarity for a basic Flask lab

## Route Design

Keep existing Caesar routes unchanged.

Add new `GET` routes:

- `/playfair`
- `/railfence`
- `/transposition`
- `/vigenere`

Add new `POST` routes:

- `/playfair/encrypt`
- `/playfair/decrypt`
- `/railfence/encrypt`
- `/railfence/decrypt`
- `/transposition/encrypt`
- `/transposition/decrypt`
- `/vigenere/encrypt`
- `/vigenere/decrypt`

Each `POST` route will:

1. Read submitted form values from `request.form`
2. Convert numeric keys with `int(...)` where required
3. Instantiate the corresponding cipher class
4. Call the verified encrypt/decrypt method
5. Re-render the same page template with result and submitted values

## Template Design

Create four new templates:

- `templates/playfair.html`
- `templates/railfence.html`
- `templates/transposition.html`
- `templates/vigenere.html`

Each page will follow the current Caesar page structure:

- Bootstrap 4.6.2 stylesheet
- centered page title such as `PLAYFAIR CIPHER`
- `ENCRYPTION` section
- `DECRYPTION` section
- one form per section
- readonly text input for result
- Jinja2 expressions to preserve form values after submit

The new templates will intentionally stay close to the current `table`-based layout and inline styling used by `caesar.html` so the UI remains visually consistent across all cipher pages.

## Form Fields

### Playfair

Encryption form:

- `plain_text`
- `key`

Decryption form:

- `cipher_text`
- `key`

Server behavior:

- create matrix with `create_playfair_matrix(key)`
- encrypt with `playfair_encrypt(plain_text, matrix)`
- decrypt with `playfair_decrypt(cipher_text, matrix)`

### Rail Fence

Encryption form:

- `plain_text`
- integer `key`

Decryption form:

- `cipher_text`
- integer `key`

Server behavior:

- encrypt with `rail_fence_encrypt(plain_text, key)`
- decrypt with `rail_fence_decrypt(cipher_text, key)`

### Transposition

Encryption form:

- `plain_text`
- integer `key`

Decryption form:

- `cipher_text`
- integer `key`

Server behavior:

- encrypt with `encrypt(plain_text, key)`
- decrypt with `decrypt(cipher_text, key)`

### Vigenere

Encryption form:

- `plain_text`
- string `key`

Decryption form:

- `cipher_text`
- string `key`

Server behavior:

- encrypt with `vigenere_encrypt(plain_text, key)`
- decrypt with `vigenere_decrypt(cipher_text, key)`

## Index Page Change

Update `templates/index.html` to include links for:

- Caesar Cipher
- Playfair Cipher
- Railfence Cipher
- Transposition Cipher
- Vigenere Cipher

No route will be added for RSA as part of this task.

## Error Handling

This task will follow the current project style and rely on HTML `required` inputs for basic validation.

For key handling:

- Playfair and Vigenere keys stay as strings
- Rail Fence and Transposition keys are parsed as integers in the route handlers

No additional validation or flash messaging will be introduced in this change, because that would expand scope beyond the requested parity with the existing Caesar implementation.

## Testing Plan

Verification will focus on local functional checks:

- `py .\app.py` starts successfully
- each new `GET` route renders
- each encrypt route returns the same page with populated result
- each decrypt route returns the same page with populated result
- Caesar routes still work after the change

## Out of Scope

These items are explicitly excluded:

- refactoring Caesar into a shared generic template
- adding JavaScript or AJAX
- changing the `cipher/` folder structure
- redesigning the current visual style
- adding advanced validation or error banners
