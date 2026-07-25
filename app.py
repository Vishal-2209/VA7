from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gh')
def github_redirect():
    return redirect('https://github.com/Vishal-2209')

@app.route('/ln')
def linkedin_redirect():
    return redirect('https://linkedin.com/in/vishal-aidasani')

@app.route('/x')
def x_redirect():
    return redirect('https://x.com/Vi27888Vishal')

@app.route('/resume')
@app.route('/cv')
def resume_redirect():
    return app.send_static_file('Vishal_Aidasani_Resume.pdf')

@app.route('/mail')
def mail_redirect():
    return redirect('mailto:primus@va7.dev')

@app.route('/ig')
def instagram_redirect():
    return redirect('https://instagram.com/vishal.aidasani_')

@app.route('/wa')
def whatsapp_redirect():
    return redirect('https://wa.me/918000516769')

@app.route('/phone')
def phone_redirect():
    return redirect('tel:+918000516769')

@app.route('/portfolio')
def portfolio_redirect():
    return redirect('https://vishal-aidasani.in')

@app.route('/blog')
@app.route('/labs')
def future_redirect():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
