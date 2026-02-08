from algopy import ARC4Contract, UInt64, arc4, Global, Txn, gtxn, itxn, BoxMap, Account, String

class GenericWhaleMarket(ARC4Contract):
    def __init__(self) -> None:
        # User Stakes (Actual VOI)
        self.stakes_a = BoxMap(Account, UInt64)
        self.stakes_b = BoxMap(Account, UInt64)
        
        # Market Metadata
        self.market_name = String("")
        self.label_a = String("")
        self.label_b = String("")
        
        # Market State
        self.total_a_pool = UInt64(0)
        self.total_b_pool = UInt64(0)
        self.is_resolved = False
        self.winner = UInt64(0) # 1 = Side A, 2 = Side B
        
        # Constants
        self.house_fee_bp = UInt64(200) # 2% House Fee
        self.mbr_cost = UInt64(50_000)  # 0.05 VOI storage fee

    @arc4.abimethod
    def initialize_market(self, name: String, a_name: String, b_name: String) -> None:
        """Sets the event details. Creator only, call once after deploy."""
        assert Txn.sender == Global.creator_address, "Only creator can init"
        assert self.market_name == String(""), "Already initialized"
        self.market_name = name
        self.label_a = a_name
        self.label_b = b_name

    @arc4.abimethod
    def bet(self, payment: gtxn.PaymentTransaction, side_a: arc4.Bool) -> None:
        """Users bet on Side A (True) or Side B (False)."""
        assert not self.is_resolved, "Market is closed"
        assert payment.receiver == Global.current_application_address, "Wrong receiver"
        
        # Determine if we need to deduct the one-time 0.05 VOI storage fee
        is_new = Txn.sender not in self.stakes_a and Txn.sender not in self.stakes_b
        net_bet = payment.amount
        
        if is_new:
            assert payment.amount > self.mbr_cost, "Bet must cover 0.05 VOI storage"
            net_bet = payment.amount - self.mbr_cost

        if side_a.native:
            current = self.stakes_a.get(Txn.sender, default=UInt64(0))
            self.stakes_a[Txn.sender] = current + net_bet
            self.total_a_pool += net_bet
        else:
            current = self.stakes_b.get(Txn.sender, default=UInt64(0))
            self.stakes_b[Txn.sender] = current + net_bet
            self.total_b_pool += net_bet

    @arc4.abimethod
    def resolve(self, winner_code: UInt64) -> None:
        """Creator declares the winner (1 or 2)."""
        assert Txn.sender == Global.creator_address, "Only creator can resolve"
        assert not self.is_resolved, "Already resolved"
        assert winner_code == UInt64(1) or winner_code == UInt64(2), "Invalid winner code"
        self.winner = winner_code
        self.is_resolved = True

    @arc4.abimethod
    def claim(self) -> None:
        """Winners claim their share of the total pool."""
        assert self.is_resolved, "Market not resolved yet"
        
        total_pool = self.total_a_pool + self.total_b_pool
        # Calculate 2% house cut
        fee = (total_pool * self.house_fee_bp) // 10_000
        payout_pool = total_pool - fee

        user_stake = UInt64(0)
        winning_side_pool = UInt64(0)

        if self.winner == UInt64(1):
            winning_side_pool = self.total_a_pool
            if Txn.sender in self.stakes_a:
                user_stake = self.stakes_a[Txn.sender]
                del self.stakes_a[Txn.sender]
        else:
            winning_side_pool = self.total_b_pool
            if Txn.sender in self.stakes_b:
                user_stake = self.stakes_b[Txn.sender]
                del self.stakes_b[Txn.sender]

        assert user_stake > 0, "No winning stake found"
        
        # Payout = (Your Bet / Total Bets on Winning Side) * Total Pool (minus fee)
        payout = (user_stake * payout_pool) // winning_side_pool
        
        itxn.Payment(
            receiver=Txn.sender,
            amount=payout,
            fee=0
        ).submit()

    @arc4.abimethod
    def withdraw_house_profit(self) -> None:
        """Creator withdraws the 2% fee and reclaimed MBR deposits."""
        assert Txn.sender == Global.creator_address
        assert self.is_resolved
        
        # Sweep all funds except a tiny 0.1 VOI buffer for contract's own MBR
        current_bal = Global.current_application_address.balance
        assert current_bal > 100_000, "Insufficient funds to withdraw"
        
        itxn.Payment(
            receiver=Txn.sender,
            amount=current_bal - 100_000,
            fee=0
        ).submit()