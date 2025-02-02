import asyncio
from web3 import Web3
from decimal import Decimal
from app.core.config import settings
from app.core.logger import logger
from app.repositories.monitored_repository import MonitoredRepository
from app.repositories.wallet_repository import WalletRepository
from app.services.transaction_service import TransactionService
from app.utils.encryption import decrypt_wallet_address
from web3.middleware import ExtraDataToPOAMiddleware

BSC_NODE_URL = settings.BSC_MAINNET_NODE_URL  # BSC 主網節點 URL
USDT_CONTRACT_ADDRESS = settings.USDT_CONTRACT_ADDRESS  # USDT 合約地址
TRANSFER_METHOD_ID = settings.TRANSFER_METHOD_ID  # 轉帳方法 ID
CORE_WALLET_ADDRESS = settings.CORE_WALLET_ADDRESS  # 核心錢包地址
CORE_WALLET_PRIVATE_KEY = settings.CORE_WALLET_PRIVATE_KEY  # 核心錢包私鑰

USDT_CONTRACT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

DEPOSIT_FEE = Decimal("0.00")  # 手續費
DEPOSIT_LIMIT = Decimal("10")  # 最低入金限制


class MonitorService:

    def __init__(
        self,
        monitored_repository: MonitoredRepository,
        wallet_repository: WalletRepository,
        transaction_service: TransactionService,
    ):
        """
        初始化監聽服務
        """
        self.web3 = Web3(Web3.HTTPProvider(BSC_NODE_URL))

        # 添加 POA 中間件
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if not self.web3.is_connected():
            raise ConnectionError("Unable to connect to the blockchain node.")

        self.monitored_repository = monitored_repository
        self.wallet_repository = wallet_repository
        self.transaction_service = transaction_service
        self.monitored_addresses = set()  # 使用 set 儲存地址，避免重複

    async def refresh_addresses(self, interval: int = 15):
        """
        定期刷新需要監聽的地址列表
        """
        while True:
            try:
                addresses = (
                    self.monitored_repository.get_all_addresses()
                )  # 從 repository 獲取所有地址
                new_addresses = {address.lower() for address in addresses}

                # 計算新加入的地址
                added_addresses = new_addresses - self.monitored_addresses

                # 更新地址列表
                self.monitored_addresses = new_addresses
                # 印出新加入的地址（如果有）
                if added_addresses:
                    logger.info(f"New monitored addresses: {added_addresses}")

            except Exception as e:
                logger.error(f"Error refreshing addresses: {e}")
            await asyncio.sleep(interval)  # 每隔 interval 秒刷新一次

    async def monitor_blockchain(self):
        """
        監聽區塊鏈，檢測是否有交易發生到監聽地址
        """
        latest_block = self.web3.eth.block_number
        logger.info(f"Starting monitoring from block: {latest_block}")

        while True:
            try:
                # 確保區塊號不超出最新區塊
                current_block = self.web3.eth.block_number
                if latest_block > current_block:
                    await asyncio.sleep(2)
                    continue

                # 查詢並處理區塊
                await self.process_block(latest_block)

                latest_block += 1  # 移動到下一個區塊
            except ConnectionError as ce:
                logger.error(f"Connection error: {ce}. Retrying in 5 seconds...")
                await asyncio.sleep(5)  # 等待後重新嘗試
            except Exception as e:
                logger.error(f"Unexpected error: {e}. Retrying in 1 second...")
                await asyncio.sleep(1)  # 控制頻率

    async def process_block(self, block_number: int):
        """
        查詢並處理指定區塊的交易
        """
        block = self.web3.eth.get_block(block_number, full_transactions=True)

        for tx in block.transactions:
            # 檢查是否是 USDT 合約的交易
            if tx.to and tx.to.lower() == USDT_CONTRACT_ADDRESS.lower():
                await self.process_transaction(tx)

    async def process_transaction(self, tx):
        """
        處理單筆交易
        """
        # 先檢查 input 存在且長度是否足夠 (至少 68 bytes)
        # 4 bytes: methodID, 32 bytes: to_address, 32 bytes: amount
        if tx.input and len(tx.input) >= 68:
            method_id = f"0x{tx.input[:4].hex()}"
            if method_id == TRANSFER_METHOD_ID:
                tx_hash = f"0x{tx.hash.hex()}"

                # 解析 to_address
                #   前 4 bytes = method ID
                #   接下來 32 bytes (offset 4:36) 存 address
                to_address_bytes = tx.input[4:36]
                to_address = f"0x{to_address_bytes.hex()[-40:]}".lower()

                # 解析 amount (offset 36:68)
                amount_bytes = tx.input[36:68]
                if not amount_bytes:
                    # amount_bytes 可能是空的 => 長度不夠
                    logger.warning(
                        f"[SKIP] TxHash={tx_hash} input length insufficient for amount."
                    )
                    return

                try:
                    amount = int(amount_bytes.hex(), 16)
                except ValueError as ve:
                    logger.warning(f"[SKIP] TxHash={tx_hash} invalid amount hex: {ve}")
                    return

                # 檢查是否為監聽地址
                if to_address in self.monitored_addresses:
                    logger.info(
                        f"[USDT TRANSFER] TxHash: {tx_hash}, "
                        f"From: {tx['from']}, "
                        f"To: {to_address}, "
                        f"Amount: {self.web3.from_wei(amount, 'ether')} USDT"
                    )

                    # 查詢該地址 USDT 餘額
                    usdt_contract = self.web3.eth.contract(
                        address=Web3.to_checksum_address(USDT_CONTRACT_ADDRESS),
                        abi=USDT_CONTRACT_ABI,
                    )
                    balance = usdt_contract.functions.balanceOf(
                        Web3.to_checksum_address(to_address)
                    ).call()
                    balance_in_ether = self.web3.from_wei(balance, "ether")

                    # 如果餘額小於指定限制，跳過處理
                    if balance_in_ether < int(DEPOSIT_LIMIT):
                        logger.info(
                            f"[USDT TRANSFER IGNORED] Address: {to_address}, "
                            f"Balance: {balance_in_ether} USDT (< {int(DEPOSIT_LIMIT)} USDT)"
                        )
                        return

                    await self.handle_deposit(
                        tx_hash, to_address, amount=balance_in_ether
                    )
        else:
            # 不是 transfer 或是 input 長度不足，直接跳過
            return

    async def handle_deposit(self, tx_hash: str, to_address: str, amount: Decimal):
        """
        處理入金邏輯，寫入資料庫
        """
        sub_wallet = self.wallet_repository.get_wallet_by_address(to_address)
        if sub_wallet:
            try:
                # 執行資金轉移
                transfer_result = await self.transfer_funds_to_core_wallet(
                    to_address, amount
                )

                # 如果轉移成功，記錄入金交易
                if transfer_result:
                    self.monitored_repository.execute_deposit_transaction(
                        sub_wallet_id=sub_wallet.SubWalletID,
                        currency_id=2,  # USDT 對應的 CurrencyID
                        amount=amount,
                        fee=DEPOSIT_FEE,
                        tx_hash=tx_hash,
                    )
                    logger.info(
                        f"Deposit recorded: SubWalletID={sub_wallet.SubWalletID}, "
                        f"Amount={self.web3.from_wei(amount, 'ether')} USDT"
                    )
                else:
                    logger.error(
                        f"Transfer to core wallet failed, skipping database update."
                    )
            except Exception as db_error:
                logger.error(f"Failed to record deposit in database: {db_error}")
        else:
            logger.warning(f"No sub-wallet found for address: {to_address}")

    async def transfer_funds_to_core_wallet(
        self, from_address: str, amount: Decimal
    ) -> bool:
        """
        將 USDT 從指定地址轉移到核心錢包
        """

        # 發送少量 BNB 到該地址，以支付 Gas 費用
        try:
            gas_fee = self.calculate_fixed_gas_for_usdt_transfer()

            # 檢查該地址是否有足夠的 BNB 來支付 Gas 費用
            from_address = Web3.to_checksum_address(from_address)
            balance_in_bnb = self.web3.from_wei(
                self.web3.eth.get_balance(from_address), "ether"
            )
            send_bnb_amount = gas_fee - balance_in_bnb

            if Decimal(balance_in_bnb) <= gas_fee:
                logger.info(
                    f"Sending {send_bnb_amount} BNB to {from_address} for gas fee"
                )
                bnb_transfer_result = self.transaction_service.transfer_bnb(
                    CORE_WALLET_PRIVATE_KEY, from_address, send_bnb_amount
                )
                if not bnb_transfer_result.success:
                    logger.error(
                        f"Failed to send BNB for gas: {bnb_transfer_result.error_message}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Failed to send BNB for gas: {e}")
            return False

        # 執行 USDT 轉移
        try:
            logger.info(
                f"Transferring {self.web3.from_wei(amount, 'ether')} USDT to core wallet"
            )

            # 取得user錢包並解密私鑰
            user_wallet = self.wallet_repository.get_wallet_by_address(from_address)

            sender_private_key = decrypt_wallet_address(
                user_wallet.EncryptedPrivateKey,
                user_wallet.KeyMaterial,
                user_wallet.Salt,
            )

            usdt_transfer_result = self.transaction_service.transfer_usdt(
                sender_private_key,
                CORE_WALLET_ADDRESS,
                amount,
            )
            if usdt_transfer_result.success:
                logger.info(
                    f"Funds transferred to core wallet. TxHash: {usdt_transfer_result.tx_hash}"
                )
                return True
            else:
                logger.error(
                    f"Failed to transfer USDT: {usdt_transfer_result.error_message}"
                )
                return False
        except Exception as e:
            logger.error(f"Failed to transfer USDT to core wallet: {e}")
            return False

    def calculate_fixed_gas_for_usdt_transfer(self) -> Decimal:
        """
        計算 USDT 轉移操作所需的 BNB（Gas 費用）。

        :return: 所需的 BNB 金額
        """
        try:
            # USDT 轉移的固定 Gas Limit
            gas_limit = 60000  # 預估的固定 Gas 使用量

            # 獲取當前的 Gas Price（單位：wei）
            gas_price = self.web3.eth.gas_price

            # 計算總 Gas 費用（單位：wei）
            total_gas_cost_in_wei = gas_limit * gas_price

            # 將總 Gas 費用轉換為 BNB
            total_gas_cost_in_bnb = self.web3.from_wei(total_gas_cost_in_wei, "ether")

            # 返回所需的 BNB 金額，保留 8 位小數
            return Decimal(total_gas_cost_in_bnb).quantize(Decimal("0.00000001"))
        except Exception as e:
            logger.error(f"無法計算 Gas 費用: {e}")
            return Decimal("0")
