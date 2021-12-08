from dataclasses import dataclass

@dataclass
class Item:
    name: str
    index: int
    cost: int

    @property
    def sell_price(self) -> int:
        return self.cost // 2
