from web3 import Web3
from decimal import Decimal
from app.core.config import settings

# 環境變數設定
BSC_NODE_URL = settings.BSC_MAINNET_NODE_URL

# BEP-20 代幣的標準 ABI
BEP20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]

# 預設代幣清單（包括 BNB 和 USDT）
TOKEN_LIST = [
    {"symbol": "BNB", "address": None},
    {"symbol": "USDT", "address": settings.USDT_CONTRACT_ADDRESS},
]


class WalletService:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(BSC_NODE_URL))
        if not self.web3.is_connected():
            raise ConnectionError("無法連接到 BSC 節點")

    def create_wallet(self) -> tuple[str, str]:
        """
        創建新 BEP20 子錢包，並返回地址和私鑰。
        """
        # 使用 web3 生成新錢包
        account = self.web3.eth.account.create()
        wallet_address = account.address
        private_key = account.key.hex()

        # 返回錢包資訊
        return wallet_address, private_key

    def get_asset_balances_from_blockchain(self, wallet_address: str) -> list[dict]:
        """
        查詢指定 BEP20 子錢包的所有資產餘額，包含 BNB 和 USDT。
        資產順序：USDT 優先，其他資產按順序返回。
        """
        assets = []

        for token in TOKEN_LIST:
            try:
                if token["address"] is None:  # 處理 BNB
                    balance = self.web3.eth.get_balance(wallet_address)
                    balance_in_ether = Decimal(self.web3.from_wei(balance, "ether"))
                    assets.append({"symbol": "BNB", "balance": balance_in_ether})
                else:  # 處理 BEP-20 代幣
                    contract = self.web3.eth.contract(
                        address=Web3.to_checksum_address(token["address"]),
                        abi=BEP20_ABI,
                    )
                    balance = contract.functions.balanceOf(wallet_address).call()
                    decimals = contract.functions.decimals().call()
                    balance_in_token = Decimal(balance) / Decimal(10**decimals)
                    assets.append(
                        {"symbol": token["symbol"], "balance": balance_in_token}
                    )
            except Exception as e:
                assets.append(
                    {"symbol": token["symbol"], "balance": f"Error: {str(e)}"}
                )

        # 調整順序：USDT 優先
        sorted_assets = sorted(assets, key=lambda x: x["symbol"] != "USDT")
        return sorted_assets
