from flask import Flask

app = Flask(__name__)

cars_global = ["Chevrolet", "Renault", "Ford", "Lada"]

def add_car(car_name):
    """Функция для добавления новых машин"""
    cars_global.append(car_name)

@app.route('/cars')
def show_cars():
    return ', '.join(cars_global)

add_car("Toyota")

if __name__ == '__main__':
    app.run(debug=True)