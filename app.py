from flask import Flask, render_template, request, jsonify, send_file
from io import StringIO, BytesIO
import csv
from datetime import datetime

app = Flask(__name__)

STOCK_PRICES = {
    'AAPL': 180,
    'TSLA': 250,
    'GOOGL': 140,
    'MSFT': 380,
    'AMZN': 150,
    'META': 320,
    'NVDA': 480,
    'NFLX': 450,
    'AMD': 120,
    'INTC': 45,
}

@app.route('/')
def index():
    return render_template('index.html', available_stocks=list(STOCK_PRICES.keys()))

@app.route('/api/add-stock', methods=['POST'])
def add_stock():
    data = request.json
    symbol = data.get('symbol', '').upper().strip()
    quantity = data.get('quantity', 0)

    if not symbol or quantity <= 0:
        return jsonify({'error': 'Invalid input'}), 400

    if symbol not in STOCK_PRICES:
        return jsonify({'error': f'Stock symbol "{symbol}" not found'}), 400

    price = STOCK_PRICES[symbol]
    total_value = price * quantity

    return jsonify({
        'symbol': symbol,
        'quantity': quantity,
        'price': price,
        'total_value': total_value
    })

@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    data = request.json
    stocks = data.get('stocks', [])

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Stock Symbol', 'Quantity', 'Price per Share', 'Total Value'])

    total_portfolio = 0
    for stock in stocks:
        symbol = stock['symbol']
        quantity = stock['quantity']
        price = STOCK_PRICES.get(symbol, 0)
        total_value = price * quantity
        total_portfolio += total_value
        writer.writerow([symbol, quantity, f'${price:.2f}', f'${total_value:.2f}'])

    writer.writerow([])
    writer.writerow(['Total Portfolio Value', '', '', f'${total_portfolio:.2f}'])

    output.seek(0)
    bytes_output = BytesIO(output.getvalue().encode('utf-8'))

    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'portfolio_{datetime.now().strftime("%Y-%m-%d")}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
