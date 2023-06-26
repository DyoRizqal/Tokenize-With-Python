from flask import Flask, request, jsonify
import mysql.connector
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords

# Inisialisasi NLTK
nltk.download("punkt")
nltk.download("stopwords")

# Inisialisasi stop words
stop_words = set(stopwords.words("english"))

# Inisialisasi stemmer
stemmer = SnowballStemmer("english")

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi koneksi database MySQL
db_config = {"host": "localhost", "user": "root", "password": "", "database": "bigdata"}


# Fungsi untuk melakukan koneksi ke database
def connect_to_database():
    return mysql.connector.connect(**db_config)


# Route untuk POST request
@app.route("/data/upload", methods=["POST"])
def upload_data():
    # Menerima data dari POST request
    data = request.get_json()

    # Memperoleh nama file dan teks bahasa Inggris dari data
    file_name = data.get("file_name")
    text = data.get("text")

    # Proses tokenisasi
    tokens = word_tokenize(text)

    # Proses stemming dan analisis teks
    stemmed_tokens = []
    analyzed_text = []
    for token in tokens:
        # Stemming
        stemmed_token = stemmer.stem(token)

        # Analisis teks
        if stemmed_token not in stop_words:
            stemmed_tokens.append(stemmed_token)
            analyzed_text.append(token)

    # Menyimpan data ke database
    connection = connect_to_database()
    cursor = connection.cursor()
    query = "INSERT INTO challenge (file_name, text, tokens, analyzed_text) VALUES (%s, %s, %s, %s)"
    values = (file_name, text, " ".join(stemmed_tokens), " ".join(analyzed_text))
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Data uploaded successfully"})


# Route untuk GET request
@app.route("/data/search/", methods=["GET"])
def search_data():
    # Menerima query parameter 'q' dari GET request
    search = request.args.get("q")

    # Melakukan pencarian data di database
    connection = connect_to_database()
    cursor = connection.cursor()
    query = "SELECT * FROM challenge WHERE analyzed_text LIKE %s"
    values = ("%" + search + "%",)
    cursor.execute(query, values)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    # Membuat response berdasarkan hasil pencarian
    response = []
    for result in results:
        search_id, file_name, text, tokens, analyzed_text = result
        response.append(
            {
                "search_id": search_id,
                "search_cleansing": analyzed_text,
                "total_text_unique": len(set(tokens.split())),  # Jumlah kata unik
                "total_processing_time": len(
                    analyzed_text.split()
                ),  # Jumlah kata setelah proses analisis
            }
        )

    return jsonify(response)


# Route untuk GET request (mengambil semua data)
@app.route("/data/all", methods=["GET"])
def get_all_data():
    # Melakukan pengambilan semua data dari database
    connection = connect_to_database()
    cursor = connection.cursor()
    query = "SELECT * FROM challenge"

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    # Membuat response berdasarkan hasil pengambilan semua data
    response = []
    for result in results:
        search_id, file_name, text, tokens, analyzed_text = result
        response.append(
            {
                "search_id": search_id,
                "file_name": file_name,
                "text": text,
                "tokens": tokens,
                "analyzed_text": analyzed_text,
            }
        )

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


# Menjalankan aplikasi Flask
# if __name__ == "__main__":
#     app.run(
#         host="0.0.0.0",
#         port=5000,
#         ssl_context=("path_to_ssl_cert.pem", "path_to_ssl_key.pem"),
#     )
