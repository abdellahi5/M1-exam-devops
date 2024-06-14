from flask import Flask, render_template, request, redirect, url_for
from prometheus_client import start_http_server, Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from time import time


app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

products = {
    100: {'description': 'Hot Dog', 'price': 9.00},
    101: {'description': 'Double Hot Dog', 'price': 11.00},
    102: {'description': 'X-Egg', 'price': 12.00},
    103: {'description': 'X-Salad', 'price': 13.00},
    104: {'description': 'X-Bacon', 'price': 14.00},
    105: {'description': 'X-Everything', 'price': 17.00},
    200: {'description': 'Soda Can', 'price': 5.00},
    201: {'description': 'Iced Tea', 'price': 4.00}
}

view_by_product = Counter('view_by_product', 'Number of views by product', ['product'])
duration_checkout = Histogram('duration_checkout', 'Duration of checkout method')

total_value = 0
order = []

def count_product_views(product):
    def decorator(func):
        def wrapper(*args, **kwargs):
            view_by_product.labels(product=product).inc()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/checkout', methods=['GET', 'POST'])
@duration_checkout.time()
def checkout():
    global total_value
    global order

    if request.method == 'POST':
        if 'submit_button' in request.form:
            if request.form['submit_button'] == 'Back':
                # Redirect to the checkout page
                return redirect(url_for('index'))
            elif request.form['submit_button'] == 'Finish':
                # Complete the order, resetting the variables
                final_value = total_value
                total_value = 0
                order = []
                return render_template('closure.html', final_value=final_value)

    return render_template('checkout.html', total_value=total_value, order=order)


@app.route('/', methods=['GET', 'POST'])
def index():
    global total_value
    global order

    if request.method == 'POST':
        # Get the product code from the form
        code = int(request.form['code'])

        if code in products:
            total_value += products[code]['price']
            order.append(products[code]['description'])
            message = f'{products[code]["description"]} added to the order.'
            view_by_product.labels(product=products[code]['description']).inc()

        else:
            message = 'Invalid option.'

        return render_template('index.html', products=products, message=message, order=order)

    return render_template('index.html', products=products, order=order)

if __name__ == '__main__':
    app.run(debug=True)