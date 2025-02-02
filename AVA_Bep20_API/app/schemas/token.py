class TokenData:
    def __init__(self, payload: dict):
        """
        使用 JWT 的 payload 初始化 TokenData 實例。

        :param payload: dict, 包含 JWT 的解碼內容
        """
        self.unique_name: str = payload.get("unique_name")
        self.nbf: int = payload.get("nbf")
        self.exp: int = payload.get("exp")
        self.iat: int = payload.get("iat")

    def __repr__(self):
        """
        提供 TokenData 的簡潔表示，方便調試。
        """
        return (
            f"TokenData(unique_name={self.unique_name}, "
            f"nbf={self.nbf}, exp={self.exp}, iat={self.iat})"
        )
