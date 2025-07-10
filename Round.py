from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List

class Trader:
    
    def _init_(self):
        self.position_djembes = 0  # Initialize the position for DJEMBES
        self.position_jams = 0  # Initialize the position for JAMS
        self.position_croissants = 0  # Initialize the position for CROISSANTS
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}

        # Trading rules for each product
        products = {
            "DJEMBES": {
                "acceptable_price": 13450,
                "position_limit": 60,
                "buy_condition": lambda price: price < 13450,
                "sell_condition": lambda price: price > 13450,
                "position": lambda: self.position_djembes
            },
            "JAMS": {
                "acceptable_price": 6673,
                "position_limit": 350,
                "buy_condition": lambda price: price < 6673,
                "sell_condition": lambda price: price > 6673,
                "position": lambda: self.position_jams
            },
            "CROISSANTS": {
                "acceptable_price": 4305,
                "position_limit": 250,
                "buy_condition": lambda price: price < 4305,
                "sell_condition": lambda price: price > 4305,
                "position": lambda: self.position_croissants
            }
        }

        for product in products:
            order_depth: OrderDepth = state.order_depths.get(product)
            
            if order_depth is None:
                continue
            
            orders: List[Order] = []
            acceptable_price = products[product]["acceptable_price"]
            position_limit = products[product]["position_limit"]
            buy_condition = products[product]["buy_condition"]
            sell_condition = products[product]["sell_condition"]
            position = products[product]["position"]()

            print(f"Handling product: {product}")
            print(f"Acceptable price: {acceptable_price}")
            print(f"Current position: {position}")
            print(f"Buy Order depth: {len(order_depth.buy_orders)}, Sell order depth: {len(order_depth.sell_orders)}")
            
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                best_ask = float(best_ask)
                
                # Apply the buy condition
                if buy_condition(best_ask) and position < position_limit:
                    print(f"BUY {int(best_ask_amount)}x {best_ask}")
                    orders.append(Order(product, best_ask, -int(best_ask_amount)))  # A negative value means buy
                    # Update the position after buying
                    if product == "DJEMBES":
                        self.position_djembes += int(best_ask_amount)
                    elif product == "JAMS":
                        self.position_jams += int(best_ask_amount)
                    elif product == "CROISSANTS":
                        self.position_croissants += int(best_ask_amount)

            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_bid = float(best_bid)

                # Apply the sell condition
                if sell_condition(best_bid) and position > 0:
                    print(f"SELL {int(best_bid_amount)}x {best_bid}")
                    orders.append(Order(product, best_bid, -int(best_bid_amount)))  # A negative value means sell
                    # Update the position after selling
                    if product == "DJEMBES":
                        self.position_djembes -= int(best_bid_amount)
                    elif product == "JAMS":
                        self.position_jams -= int(best_bid_amount)
                    elif product == "CROISSANTS":
                        self.position_croissants -= int(best_bid_amount)

            result[product] = orders
        
        traderData = "SAMPLE"  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 1  # Conversions, set to 1 as a placeholder

        return result, conversions, traderData