from dataclasses import dataclass


@dataclass(frozen=True)
class MarketDTO:
    symbol: str
    base_asset: str
    quote_asset: str
    display_name: str
    enabled: bool


SUPPORTED_MARKETS = (
    MarketDTO(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        display_name="BTC/USDT",
        enabled=True,
    ),
    MarketDTO(
        symbol="ETHUSDT",
        base_asset="ETH",
        quote_asset="USDT",
        display_name="ETH/USDT",
        enabled=True,
    ),
)


def list_markets() -> list[MarketDTO]:
    return list(SUPPORTED_MARKETS)
