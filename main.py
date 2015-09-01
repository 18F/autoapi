from app import make_app

app, container = make_app()

if __name__ == '__main__':
    app.run()
