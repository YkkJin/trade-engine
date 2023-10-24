from .type import EventType
from ..log_handler.default_handler import DefaultLogHandler
from collections import defaultdict


class EventEngine:

    def __init__(self, bus, log):
        self.bus = bus
        # self.strategy = strategy
        self.log = log
        self.strategy_dict = defaultdict()
        # self.quoter = quoter
        # self.trader = trader

    def run(self) -> None:

        self.log.info(f"主引擎启动")
        # self.bus.register(EventType.TICK, self.strategy.on_tick)
        # self.bus.register(EventType.TRADE, self.strategy.on_trade)
        # self.bus.register(EventType.ORDER, self.strategy.on_order)
        # self.quoter.subscribe(self.strategy.subscribe_list())
        self.bus.start()

    def load_strategy(self, strategy) -> bool:
        strategy_key = strategy.id
        if strategy_key in self.strategy_dict.keys():
            self.log.info(f"该策略{strategy.name}_{strategy_key}已添加，请添加其他策略")
            return False
        self.strategy_dict[strategy_key] = strategy
        self.bus.register(EventType.TICK, self.strategy_dict[strategy_key].on_tick)
        self.bus.register(EventType.TRADE, self.strategy_dict[strategy_key].on_trade)
        self.bus.register(EventType.ORDER, self.strategy_dict[strategy_key].on_order)
        self.bus.register(EventType.L2OrdTrac, self.strategy_dict[strategy_key].on_l2OrdTrac)
        self.bus.register(EventType.L2TICK, self.strategy_dict[strategy_key].on_l2tick)
        self.log.info(f"策略{strategy.name}_{strategy_key}添加成功！")
        return True

    def remove_strategy(self, strategy_key) -> None:
        if strategy_key not in self.strategy_dict.keys():
            self.log.info(f"未找到{strategy_key}")
        else:

            self.bus.unregister(EventType.TICK, self.strategy_dict[strategy_key].on_tick)
            self.bus.unregister(EventType.TRADE, self.strategy_dict[strategy_key].on_trade)
            self.bus.unregister(EventType.ORDER, self.strategy_dict[strategy_key].on_order)
            self.bus.unregister(EventType.L2OrdTrac, self.strategy_dict[strategy_key].on_l2OrdTrac)
            self.bus.unregister(EventType.L2TICK, self.strategy_dict[strategy_key].on_l2tick)
            self.strategy_dict.pop(strategy_key)
            self.log.info(f"策略{strategy_key}已移除")

    def check_strategy(self) -> None:
        if not self.strategy_dict:
            self.log.info("主引擎中无策略运行")
        else:
            return self.strategy_dict

    def stop(self) -> None:
        if self.strategy_dict:
            self.log.info("注销监听策略")
            for key in list(self.strategy_dict):
                self.remove_strategy(key)
        self.log.info("主引擎关闭")

        # self.bus.unregister(EventType.TICK,self.strategy.on_tick)
        # self.bus.unregister(EventType.TRADE,self.strategy.on_trade)
        # self.bus.unregister(EventType.ORDER,self.strategy.on_order)
        self.bus.stop()


