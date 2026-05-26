from flask import Flask, render_template, request
from cipher.caesar import CaesarCipher
from cipher.playfair import PlayFairCipher
from cipher.railfence import RailFenceCipher
from cipher.transposition import TranspositionCipher
from cipher.vigenere import VigenereCipher

app = Flask(__name__)


# router routes for home page
@app.route("/")
def home():
    return render_template("index.html")


# router routes for caesar cipher
@app.route("/caesar")
def caesar():
    return render_template("caesar.html")


@app.route("/caesar/encrypt", methods=["POST"])
def caesar_encrypt():
    text = request.form["inputPlainText"]
    key = int(request.form["inputKeyPlain"])

    caesar_cipher = CaesarCipher()
    encrypted_text = caesar_cipher.encrypt_text(text, key)

    return render_template(
        "caesar.html",
        encrypted_text=encrypted_text,
        plain_text=text,
        encrypt_key=key,
    )


@app.route("/caesar/decrypt", methods=["POST"])
def caesar_decrypt():
    text = request.form["inputCipherText"]
    key = int(request.form["inputKeyCipher"])

    caesar_cipher = CaesarCipher()
    decrypted_text = caesar_cipher.decrypt_text(text, key)

    return render_template(
        "caesar.html",
        decrypted_text=decrypted_text,
        cipher_text=text,
        decrypt_key=key,
    )


# router routes for playfair cipher
@app.route("/playfair")
def playfair():
    return render_template("playfair.html")


@app.route("/playfair/creatematrix", methods=["POST"])
def playfair_creatematrix():
    key = request.form["inputMatrixKey"]

    playfair_cipher = PlayFairCipher()
    playfair_matrix = playfair_cipher.create_playfair_matrix(key)
    matrix_result = " | ".join(" ".join(row) for row in playfair_matrix)

    return render_template(
        "playfair.html",
        matrix_key=key,
        matrix_result=matrix_result,
    )


@app.route("/playfair/encrypt", methods=["POST"])
def playfair_encrypt():
    text = request.form["inputPlainText"]
    key = request.form["inputKeyPlain"]

    playfair_cipher = PlayFairCipher()
    playfair_matrix = playfair_cipher.create_playfair_matrix(key)
    encrypted_text = playfair_cipher.playfair_encrypt(text, playfair_matrix)

    return render_template(
        "playfair.html",
        encrypted_text=encrypted_text,
        plain_text=text,
        encrypt_key=key,
    )


@app.route("/playfair/decrypt", methods=["POST"])
def playfair_decrypt():
    text = request.form["inputCipherText"]
    key = request.form["inputKeyCipher"]

    playfair_cipher = PlayFairCipher()
    playfair_matrix = playfair_cipher.create_playfair_matrix(key)
    decrypted_text = playfair_cipher.playfair_decrypt(text, playfair_matrix)

    return render_template(
        "playfair.html",
        decrypted_text=decrypted_text,
        cipher_text=text,
        decrypt_key=key,
    )


# router routes for railfence cipher
@app.route("/railfence")
def railfence():
    return render_template("railfence.html")


@app.route("/railfence/encrypt", methods=["POST"])
def railfence_encrypt():
    text = request.form["inputPlainText"]
    key = int(request.form["inputKeyPlain"])

    railfence_cipher = RailFenceCipher()
    encrypted_text = railfence_cipher.rail_fence_encrypt(text, key)

    return render_template(
        "railfence.html",
        encrypted_text=encrypted_text,
        plain_text=text,
        encrypt_key=key,
    )


@app.route("/railfence/decrypt", methods=["POST"])
def railfence_decrypt():
    text = request.form["inputCipherText"]
    key = int(request.form["inputKeyCipher"])

    railfence_cipher = RailFenceCipher()
    decrypted_text = railfence_cipher.rail_fence_decrypt(text, key)

    return render_template(
        "railfence.html",
        decrypted_text=decrypted_text,
        cipher_text=text,
        decrypt_key=key,
    )


# router routes for transposition cipher
@app.route("/transposition")
def transposition():
    return render_template("transposition.html")


@app.route("/transposition/encrypt", methods=["POST"])
def transposition_encrypt():
    text = request.form["inputPlainText"]
    key = int(request.form["inputKeyPlain"])

    transposition_cipher = TranspositionCipher()
    encrypted_text = transposition_cipher.encrypt(text, key)

    return render_template(
        "transposition.html",
        encrypted_text=encrypted_text,
        plain_text=text,
        encrypt_key=key,
    )


@app.route("/transposition/decrypt", methods=["POST"])
def transposition_decrypt():
    text = request.form["inputCipherText"]
    key = int(request.form["inputKeyCipher"])

    transposition_cipher = TranspositionCipher()
    decrypted_text = transposition_cipher.decrypt(text, key)

    return render_template(
        "transposition.html",
        decrypted_text=decrypted_text,
        cipher_text=text,
        decrypt_key=key,
    )


# router routes for vigenere cipher
@app.route("/vigenere")
def vigenere():
    return render_template("vigenere.html")


@app.route("/vigenere/encrypt", methods=["POST"])
def vigenere_encrypt():
    text = request.form["inputPlainText"]
    key = request.form["inputKeyPlain"]

    vigenere_cipher = VigenereCipher()
    encrypted_text = vigenere_cipher.vigenere_encrypt(text, key)

    return render_template(
        "vigenere.html",
        encrypted_text=encrypted_text,
        plain_text=text,
        encrypt_key=key,
    )


@app.route("/vigenere/decrypt", methods=["POST"])
def vigenere_decrypt():
    text = request.form["inputCipherText"]
    key = request.form["inputKeyCipher"]

    vigenere_cipher = VigenereCipher()
    decrypted_text = vigenere_cipher.vigenere_decrypt(text, key)

    return render_template(
        "vigenere.html",
        decrypted_text=decrypted_text,
        cipher_text=text,
        decrypt_key=key,
    )


# main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
