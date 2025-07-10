from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict

class Trader:
    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        traderData = "v1"  # Optional versioning or state data
        conversions = 0  # Not using conversion in this strategy

        CSI = 20.5
        PRODUCT = "MACARON"
        POSITION_LIMIT = 75

        if PRODUCT not in state.order_depths:
            return {}, conversions, traderData

        order_depth: OrderDepth = state.order_depths[PRODUCT]
        orders: List[Order] = []
        position = state.position.get(PRODUCT, 0)

        # Observations (for sunlightIndex, transport fees, tariffs)
        obs = state.observations.get(PRODUCT, None)
        if obs is None:
            return {}, conversions, traderData

        sunlight = obs.sunlight
        import_tariff = obs.importTariff
        export_tariff = obs.exportTariff
        transport_fee = obs.transportFees

        # BUY logic
        if sunlight < CSI and position < POSITION_LIMIT:
            # Sort asks lowest to highest
            for ask_price in sorted(order_depth.sell_orders.keys()):
                volume = -order_depth.sell_orders[ask_price]
                buy_qty = min(volume, POSITION_LIMIT - position)
                total_cost = ask_price + import_tariff + transport_fee
                orders.append(Order(PRODUCT, ask_price, buy_qty))
                position += buy_qty
                if position >= POSITION_LIMIT:
                    break

        # SELL logic
        elif sunlight > CSI and position > -POSITION_LIMIT:
            # Sort bids highest to lowest
            for bid_price in sorted(order_depth.buy_orders.keys(), reverse=True):
                volume = order_depth.buy_orders[bid_price]
                sell_qty = min(volume, position + POSITION_LIMIT)
                total_proceeds = bid_price - export_tariff - transport_fee
                orders.append(Order(PRODUCT, bid_price, -sell_qty))
                position -= sell_qty
                if position <= -POSITION_LIMIT:
                    break

        result[PRODUCT] = orders
        return result, conversions, traderData