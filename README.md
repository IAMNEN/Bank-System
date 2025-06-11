# 🏦 Bank System Project

A full-featured **banking system** built in **Python** with **MongoDB**, designed to simulate real-world banking operations like account creation, deposits, withdrawals, transfers, loan management, interest application, and transaction history.

---

## 🚀 Features

- 👤 **Create Account**  
- 💰 **Deposit / Withdraw Funds**  
- 🔁 **Transfer Between Accounts**  
- 📊 **Check Balance**  
- 🧾 **Transaction History**  
- 💸 **Apply Interest (Custom Rate)**  
- 📄 **Loan Issuance & Repayment**  
- 🧮 **Monthly Payment Calculation**  

---

## 🧠 Technologies Used

- 🐍 Python 3
- 🍃 MongoDB
- 🔗 `pymongo` for database connectivity
- 🕹️ Command-Line Interface (CLI)

---

## 🛠️ Setup Instructions

1. 🔽 **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/bank-system.git
   cd bank-system
   ```

2. 📦 **Install Dependencies**
   ```bash
   pip install pymongo
   ```

3. 🧩 **Make Sure MongoDB is Running**  
   You can use a local MongoDB instance (default: `mongodb://localhost:27017/`)

4. ▶️ **Run the Application**
   ```bash
   python Bank-System.py
   ```

---

## 📋 Menu Options

| Option | Description                |
|--------|----------------------------|
| 1️⃣     | Create Account             |
| 2️⃣     | Deposit                    |
| 3️⃣     | Withdraw                   |
| 4️⃣     | Check Balance              |
| 5️⃣     | Transfer Between Accounts |
| 6️⃣     | View Transaction History   |
| 7️⃣     | Apply Interest             |
| 8️⃣     | Apply for Loan             |
| 9️⃣     | Repay Loan                 |
| 🔟     | View Loans                 |
| 🔚     | Exit                        |

---

## 🧪 Example Commands

```text
✅ Account ACC100001 created for Alice with balance $1000.00
✅ Deposited $500.00. New balance: $1500.00
✅ Transferred $200.00 from ACC100001 to ACC100002
✅ Loan of $1000 granted. Total to repay: $1050.00
✅ Payment accepted. Remaining balance: $525.00
```

---

## 📦 Database Collections

- `accounts` – user account info (number, name, balance)
- `transactions` – logs of all actions
- `loans` – active and past loans
- `counters` – account number generator

---

## ✅ To-Do / Enhancements

- 🔐 Add user authentication
- 🌐 Build a web interface (Flask/FastAPI)
- 📱 Add SMS/email notifications
- 🧪 Write unit tests

---

## 📄 License

MIT License © 2025 Nen

---

## 🙌 Acknowledgements

Built with ❤️ and Python.
