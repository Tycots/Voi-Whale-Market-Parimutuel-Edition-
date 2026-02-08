🐋 Voi Whale Market (Generic Parimutuel Edition)
A decentralized, open-source prediction market built on the Voi Network. This contract uses a Parimutuel (Pool-Based) model, ensuring the house never goes broke and winners always split the pool fairly.

🚀 Features

Generic Setup: Use the same contract for any 2-sided event (Sports, Elections, Price Action).

Mathematical Safety: Payouts are pro-rata based on the actual VOI in the vault.

Self-Cleaning: Storage boxes are deleted upon claiming, reclaiming MBR for the network.

Creator-Led: The market creator initializes and resolves the market.

🧮 How the Math Works

Unlike fixed-odds betting, this contract uses a Betting Pool.

Total Pool = All VOI deposited by everyone.

House Fee = 2% is deducted from the Total Pool upon resolution.

The Payout = Winners split the remaining 98% based on their % share of the winning side.

🛠️ Developer Guide

1. Deployment & Initialization

Deploy the GenericWhaleMarket contract, then call initialize_market:

name: "Super Bowl LIX"

a_name: "Seahawks"

b_name: "Patriots"

2. Seeding the Odds

To set initial "Price" or "Odds," the creator should place the first bets.

To set 31/69 Odds: Bet 310 VOI on Side A and 690 VOI on Side B.

Note: Add 0.05 VOI to your very first bet to cover the one-time Storage MBR.

3. The "Claim Fee" (Crucial)

Because the contract uses an Inner Transaction to pay winners, the caller must provide enough fee for both the App Call and the Payment.

Set Flat Fee: 2,000 microVoi (0.002 VOI)

If you set the standard 0.001 fee, the transaction will fail.

📜 License

This project is licensed under the MIT License—feel free to fork, bet, and build!
