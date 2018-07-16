from app_core import app
#from werkzeug.contrib.fixers import ProxyFix
#app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=2)

if __name__ == "__main__":
    app.run(port=8000, debug=True, use_reloader=True)
