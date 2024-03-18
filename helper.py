class Helper:
    @staticmethod
    def calculate_total_order_price(items):
        total_price = 0
        for item in items:
            total_price += item.price
        total_price = round(total_price, 2)  # round to 2 decimal places
        print(total_price)
        return total_price