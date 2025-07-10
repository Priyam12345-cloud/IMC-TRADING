import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any

class Logger:
    def _init_(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        return [[l.symbol, l.product, l.denomination] for l in listings.values()]

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        return {symbol: [od.buy_orders, od.sell_orders] for symbol, od in order_depths.items()}

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        return [[t.symbol, t.price, t.quantity, t.buyer, t.seller, t.timestamp] for arr in trades.values() for t in arr]

    def compress_observations(self, observations: Observation) -> list[Any]:
        return [
            observations.plainValueObservations,
            {p: [o.bidPrice, o.askPrice, o.transportFees, o.exportTariff, o.importTariff, o.sunlight, o.humidity]
             for p, o in observations.conversionObservations.items()}
        ]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        return [[o.symbol, o.price, o.quantity] for arr in orders.values() for o in arr]

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        return value if len(value) <= max_length else value[:max_length - 3] + "..."

logger = Logger()

class Trader:
    def _init_(self):
        self.rules = {
            "CROISSANTS": ((4303, 4305), (4305, 4307), 250),
            "DJEMBES": ((13443, 13445), (13445, 13456), 60),
            "JAMS": ((6669, 6672), (6672.5, 6674), 350),
            "KELP": ((2023, 2025), (2025.5, 2026), 50),
            "RAINFOREST_RESIN": ((9996, 9999), (10000, 10003), 50),
            "SQUID_INK": ((2005, 2006), (2008, 2012), 50),
            "PICNIC_BASKET1": ((59296, 59319), (59324, 59329), 60),
            "PICNIC_BASKET2": ((30603, 30612), (30613, 30618), 100),
        }

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        result = {}
        conversions = 0
        trader_data = ""

        for product, order_depth in state.order_depths.items():
            if product not in self.rules:
                continue

            buy_range, sell_range, pos_limit = self.rules[product]
            position = state.position.get(product, 0)
            orders = []

            # Buy logic
            for ask_price, ask_volume in sorted(order_depth.sell_orders.items()):
                if buy_range[0] <= ask_price <= buy_range[1] and position < pos_limit:
                    buy_volume = min(ask_volume, pos_limit - position)
                    logger.print(f"BUY {buy_volume}x {ask_price} for {product}")
                    orders.append(Order(product, ask_price, buy_volume))
                    position += buy_volume

            # Sell logic
            for bid_price, bid_volume in sorted(order_depth.buy_orders.items(), reverse=True):
                if sell_range[0] <= bid_price <= sell_range[1] and position > -pos_limit:
                    sell_volume = min(bid_volume, pos_limit + position)
                    logger.print(f"SELL {sell_volume}x {bid_price} for {product}")
                    orders.append(Order(product, bid_price, -sell_volume))
                    position -= sell_volume

            result[product] = orders

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data