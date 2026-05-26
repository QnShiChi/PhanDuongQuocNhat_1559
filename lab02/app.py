from flask import Flask, render_template, request
from cipher.caesar import CaesarCipher

app = Flask(__name__)


# router routes for home page
@app.route("/")
def home():
    return render_template('index.html')


# router routes for caesar cipher
@app.route("/caesar")
def caesar():
    return render_template('caesar.html')


@app.route("/caesar/encrypt", methods=['POST'])
def caesar_encrypt():
    text = request.form['inputPlainText']
    key = int(request.form['inputKeyPlain'])

    Caesar = CaesarCipher()
    encrypted_text = Caesar.encrypt_text(text, key)

    return render_template(
        'caesar.html',
        encrypted_text=encrypted_text,
        plain_text=text,
        encrypt_key=key
    )


@app.route("/caesar/decrypt", methods=['POST'])
def caesar_decrypt():
    text = request.form['inputCipherText']
    key = int(request.form['inputKeyCipher'])

    Caesar = CaesarCipher()
    decrypted_text = Caesar.decrypt_text(text, key)

    return render_template(
        'caesar.html',
        decrypted_text=decrypted_text,
        cipher_text=text,
        decrypt_key=key
    )


# main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)