from app import app

# Asegurarse de que la aplicación está configurada para producción
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

if __name__ == "__main__":
    app.run() 