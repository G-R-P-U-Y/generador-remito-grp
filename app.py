from flask import Flask, render_template, request, send_file
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import tempfile
import datetime
import os

app = Flask(__name__)
remito_counter_file = "remito_counter.txt"

def get_next_remito_number():
    if not os.path.exists(remito_counter_file):
        with open(remito_counter_file, "w") as f:
            f.write("1")
        return "01"
    with open(remito_counter_file, "r+") as f:
        number = int(f.read().strip()) + 1
        f.seek(0)
        f.write(str(number))
        f.truncate()
        return str(number).zfill(2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        today = datetime.datetime.today().strftime("%d/%m/%Y")
        numero = get_next_remito_number()
        data = {
            "fecha": today,
            "numero": numero,
            "destinatario": request.form["destinatario"],
            "direccion": request.form["direccion"],
            "descripcion": request.form["descripcion"],
            "cantidad": request.form["cantidad"],
            "observaciones": request.form["observaciones"],
            "entregado": request.form["entregado"],
            "recibido": request.form["recibido"],
        }

        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("remito_template.html")
        html_out = template.render(data=data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            HTML(string=html_out, base_url=".").write_pdf(tmp_pdf.name)
            return send_file(tmp_pdf.name, as_attachment=True, download_name=f"remito_{numero}.pdf")

    return render_template("formulario.html")

if __name__ == "__main__":
    app.run(debug=True)
