# Python Cipher Lab Project

This repository contains practice exercises for `lab01` and `lab02`.

`lab01` includes basic Python exercises.

`lab02/ex01` implements a small Flask API for two classic ciphers:
- Caesar Cipher
- Vigenere Cipher

## Project Structure

```text
.
|-- lab01/
|   |-- ex_01/
|   |-- ex_02/
|   |-- ex_03/
|   `-- ex_04/
|-- lab02/
|   `-- ex01/
|       |-- api.py
|       |-- requirements.txt
|       `-- cipher/
|           |-- caesar/
|           `-- vigenere/
`-- README.md
```

## Requirements

- Python 3.10 or newer
- `pip`

## Installation

From the project root:

```bash
cd lab02/ex01
pip install -r requirements.txt
```

## Run The API

```bash
cd lab02/ex01
python api.py
```

The server starts at:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Caesar Cipher

Encrypt:

```http
POST /api/caesar/encrypt
Content-Type: application/json
```

Example body:

```json
{
  "plain_text": "HELLO",
  "key": 3
}
```

Decrypt:

```http
POST /api/caesar/decrypt
Content-Type: application/json
```

Example body:

```json
{
  "cipher_text": "KHOOR",
  "key": 3
}
```

### Vigenere Cipher

Encrypt:

```http
POST /api/vigenere/encrypt
Content-Type: application/json
```

Example body:

```json
{
  "plain_text": "HELLO",
  "key": "KEY"
}
```

Decrypt:

```http
POST /api/vigenere/decrypt
Content-Type: application/json
```

Example body:

```json
{
  "cipher_text": "RIJVS",
  "key": "KEY"
}
```

## Example With `curl`

```bash
curl -X POST http://127.0.0.1:5000/api/caesar/encrypt \
  -H "Content-Type: application/json" \
  -d "{\"plain_text\":\"HELLO\",\"key\":3}"
```

## Notes

- Caesar Cipher currently works with uppercase English letters.
- Vigenere Cipher preserves letter case and keeps non-alphabet characters unchanged.
- The Flask app runs in debug mode in the current implementation.
