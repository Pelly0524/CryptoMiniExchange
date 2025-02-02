from web3 import Web3
from datetime import datetime
from decimal import Decimal
from app.core.config import settings
from app.schemas.transaction import TransactionResult

BSC_NODE_URL = settings.BSC_MAINNET_NODE_URL
USDT_CONTRACT_ADDRESS = settings.USDT_CONTRACT_ADDRESS
CORE_WALLET_PRIVATE_KEY = settings.CORE_WALLET_PRIVATE_KEY


class TransactionService:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(BSC_NODE_URL))
        if not self.web3.is_connected():
            raise ConnectionError("無法連接到 BSC 節點")

    def transfer_usdt(
        self, sender_private_key, recipient_address, amount: Decimal
    ) -> TransactionResult:
        """
        從用戶的錢包中轉帳 USDT 到其他用戶的錢包

        :param sender_private_key: 發送方的私鑰
        :param recipient_address: 接收方地址
        :param amount: 發送 USDT 的數量(注意是美金單位)
        """
        try:
            # 將輸入的 USDT 金額轉換為最小單位
            amount_in_wei = self.web3.to_wei(amount, "ether")  # 將 USDT 轉換為最小單位

            # 確保地址是 checksum 地址
            contract_address = Web3.to_checksum_address(USDT_CONTRACT_ADDRESS)
            recipient_address = Web3.to_checksum_address(recipient_address)

            # 準備合約 ABI（這裡假設 USDT 的標準 ERC20 ABI）
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_to", "type": "address"},
                        {"name": "_value", "type": "uint256"},
                    ],
                    "name": "transfer",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function",
                }
            ]

            # 建立合約物件
            contract = self.web3.eth.contract(address=contract_address, abi=erc20_abi)

            # 發送交易前獲取 nonce 值
            sender_address = self.web3.eth.account.from_key(sender_private_key).address
            nonce = self.web3.eth.get_transaction_count(sender_address)

            # 準備交易的輸入數據（用於估算 gas）
            transfer_function = contract.functions.transfer(
                recipient_address, amount_in_wei
            )

            # 設定 gas price
            gas_price = self.web3.eth.gas_price
            gas_limit = transfer_function.estimate_gas(
                {
                    "from": sender_address,
                    "nonce": nonce,
                    "gasPrice": gas_price,
                }
            )

            # 為了安全起見，將 gas limit 增加一些餘量（例如增加 10%）
            gas_limit = int(gas_limit * 1.1)

            # 建立交易資料
            tx = transfer_function.build_transaction(
                {
                    "chainId": 56,  # BSC 主網的 Chain ID
                    "gas": gas_limit,
                    "gasPrice": gas_price,
                    "nonce": nonce,
                    "from": sender_address,
                }
            )

            # 簽名交易
            signed_tx = self.web3.eth.account.sign_transaction(tx, sender_private_key)
            # 發送交易，使用 `signed_tx.rawTransaction` 來取得原始交易數據
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            # 獲取已使用的 gas
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            gas_used = self.web3.from_wei(tx_receipt.gasUsed * gas_price, "ether")

            # 返回交易編號
            return TransactionResult(
                success=True,
                timestamp=datetime.now().isoformat(),
                tx_hash=self.web3.to_hex(tx_hash),
                sender_address=sender_address,
                recipient_address=recipient_address,
                amount=amount,
                gas_used=gas_used.normalize(),
            )
        except Exception as e:
            return TransactionResult(
                timestamp=datetime.now().isoformat(),
                success=False,
                error_message=f"交易失敗: {str(e)}",
                sender_address=sender_address if "sender_address" in locals() else None,
                recipient_address=recipient_address,
                amount=amount,
            )

    def transfer_bnb(
        self, sender_private_key, recipient_address, amount: Decimal
    ) -> TransactionResult:
        """
        從用戶的錢包中轉帳 BNB 到其他用戶的錢包

        :param sender_private_key: 發送方的私鑰
        :param recipient_address: 接收方地址
        :param amount: 發送 BNB 的數量
        """
        try:
            # 將地址轉換為 checksum 地址
            sender_address = self.web3.eth.account.from_key(sender_private_key).address
            recipient_address = Web3.to_checksum_address(recipient_address)

            # 設定交易的 nonce 值
            nonce = self.web3.eth.get_transaction_count(sender_address)

            # 設定 gas price 和 gas limit
            gas_price = self.web3.eth.gas_price
            gas_limit = 21000  # 標準 BNB 轉帳的 gas limit

            # 使用 Web3 的內建方法轉換金額
            amount_in_wei = self.web3.to_wei(amount, "ether")

            # 建立交易資料
            tx = {
                "nonce": nonce,
                "to": recipient_address,
                "value": amount_in_wei,
                "gas": gas_limit,
                "gasPrice": gas_price,
                "chainId": 56,  # BSC 主網的 Chain ID
            }

            # 簽名交易
            signed_tx = self.web3.eth.account.sign_transaction(tx, sender_private_key)

            # 發送交易，使用 `signed_tx.rawTransaction` 來取得原始交易數據
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # 等待交易完成
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            # 使用 Web3 內建方法計算 gas used 的費用
            gas_used = self.web3.from_wei(
                tx_receipt.gasUsed * gas_price, "ether"
            )  # 轉換為 ether

            # 返回交易結果
            return TransactionResult(
                success=True,
                timestamp=datetime.now().isoformat(),
                tx_hash=self.web3.to_hex(tx_hash),
                sender_address=sender_address,
                recipient_address=recipient_address,
                amount=amount,
                gas_used=Decimal(gas_used).normalize(),
            )
        except Exception as e:
            return TransactionResult(
                timestamp=datetime.now().isoformat(),
                success=False,
                error_message=f"交易失敗: {str(e)}",
                sender_address=sender_address if "sender_address" in locals() else None,
                recipient_address=recipient_address,
                amount=amount,
            )

    def withdraw_system_usdt(
        self, recipient_address, amount: Decimal
    ) -> TransactionResult:
        """
        從核心錢包中提領 USDT 到其他用戶的地址

        :param recipient_address: 接收方地址
        :param amount: 發送 USDT 的數量
        """
        transaction_result = self.transfer_usdt(
            CORE_WALLET_PRIVATE_KEY, recipient_address, amount
        )
        return transaction_result
