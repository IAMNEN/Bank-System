from pymongo import MongoClient
from datetime import datetime
import uuid

class BankSystem:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="bank_system"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.accounts = self.db.accounts
        self.transactions = self.db.transactions
        self.loans = self.db.loans
        self.counters = self.db.counters
        self.init_counter()

    def init_counter(self):
        if not self.counters.find_one({"_id": "account_number"}):
            self.counters.insert_one({"_id": "account_number", "value": 100000})

    def generate_account_number(self):
        result = self.counters.find_one_and_update(
            {"_id": "account_number"},
            {"$inc": {"value": 1}},
            return_document=True
        )
        return f"ACC{result['value']}"

    def create_account(self, name, balance=0.0):
        acc_no = self.generate_account_number()
        self.accounts.insert_one({
            "account_number": acc_no,
            "name": name,
            "balance": balance
        })
        self.log_transaction(acc_no, "create_account", balance)
        print(f"✅ Account {acc_no} created for {name} with balance ${balance:.2f}")

    def deposit(self, acc_no, amount):
        if amount <= 0:
            print("❌ Deposit amount must be positive.")
            return
        account = self.accounts.find_one({"account_number": acc_no})
        if not account:
            print("❌ Account not found.")
            return
        new_balance = account['balance'] + amount
        self.accounts.update_one({"account_number": acc_no}, {"$set": {"balance": new_balance}})
        self.log_transaction(acc_no, "deposit", amount)
        print(f"✅ Deposited ${amount:.2f}. New balance: ${new_balance:.2f}")

    def withdraw(self, acc_no, amount):
        if amount <= 0:
            print("❌ Withdrawal amount must be positive.")
            return
        account = self.accounts.find_one({"account_number": acc_no})
        if not account:
            print("❌ Account not found.")
            return
        if account['balance'] < amount:
            print("❌ Insufficient balance.")
            return
        new_balance = account['balance'] - amount
        self.accounts.update_one({"account_number": acc_no}, {"$set": {"balance": new_balance}})
        self.log_transaction(acc_no, "withdraw", -amount)
        print(f"✅ Withdrew ${amount:.2f}. New balance: ${new_balance:.2f}")

    def transfer(self, from_acc, to_acc, amount):
        if amount <= 0:
            print("❌ Transfer amount must be positive.")
            return
        sender = self.accounts.find_one({"account_number": from_acc})
        receiver = self.accounts.find_one({"account_number": to_acc})
        if not sender or not receiver:
            print("❌ One or both accounts not found.")
            return
        if sender['balance'] < amount:
            print("❌ Insufficient funds for transfer.")
            return
        self.accounts.update_one({"account_number": from_acc}, {"$inc": {"balance": -amount}})
        self.accounts.update_one({"account_number": to_acc}, {"$inc": {"balance": amount}})
        self.log_transaction(from_acc, "transfer_out", -amount, to_acc)
        self.log_transaction(to_acc, "transfer_in", amount, from_acc)
        print(f"✅ Transferred ${amount:.2f} from {from_acc} to {to_acc}")

    def check_balance(self, acc_no):
        account = self.accounts.find_one({"account_number": acc_no})
        if account:
            print(f"💰 Balance for {account['name']} ({acc_no}): ${account['balance']:.2f}")
        else:
            print("❌ Account not found.")

    def show_transactions(self, acc_no):
        txns = self.transactions.find({"account_number": acc_no}).sort("timestamp", -1)
        print(f"📜 Transaction history for {acc_no}:")
        for txn in txns:
            print(f"{txn['timestamp']} - {txn['type']} - ${txn['amount']:.2f}", end='')
            if 'related_account' in txn:
                print(f" (related to {txn['related_account']})")
            else:
                print()

    def apply_interest(self, acc_no=None, rate=0.02):
        query = {"account_number": acc_no} if acc_no else {}
        accounts = self.accounts.find(query)
        for acc in accounts:
            interest = acc['balance'] * rate
            new_balance = acc['balance'] + interest
            self.accounts.update_one({"account_number": acc['account_number']}, {"$set": {"balance": new_balance}})
            self.log_transaction(acc['account_number'], "interest", interest)
            print(f"✅ Applied ${interest:.2f} interest to {acc['account_number']}. New balance: ${new_balance:.2f}")

    def apply_loan(self, acc_no, amount, rate, duration_months):
        account = self.accounts.find_one({"account_number": acc_no})
        if not account:
            print("❌ Account not found.")
            return
        interest = amount * rate
        total_payable = amount + interest
        monthly_payment = total_payable / duration_months
        loan = {
            "account_number": acc_no,
            "loan_id": str(uuid.uuid4())[:8],
            "amount": amount,
            "interest_rate": rate,
            "duration_months": duration_months,
            "remaining_balance": total_payable,
            "monthly_payment": monthly_payment,
            "created_at": datetime.now(),
            "status": "active"
        }
        self.loans.insert_one(loan)
        self.log_transaction(acc_no, "loan_issued", amount)
        self.accounts.update_one({"account_number": acc_no}, {"$inc": {"balance": amount}})
        print(f"✅ Loan of ${amount} granted. Total to repay: ${total_payable:.2f}")

    def repay_loan(self, acc_no, loan_id, payment):
        loan = self.loans.find_one({"loan_id": loan_id, "account_number": acc_no})
        if not loan:
            print("❌ Loan not found.")
            return
        if loan['status'] == "paid":
            print("✅ Loan already paid.")
            return
        account = self.accounts.find_one({"account_number": acc_no})
        if not account or account['balance'] < payment:
            print("❌ Insufficient account balance.")
            return
        new_balance = loan['remaining_balance'] - payment
        self.accounts.update_one({"account_number": acc_no}, {"$inc": {"balance": -payment}})
        self.log_transaction(acc_no, "loan_repayment", -payment, loan_id)
        if new_balance <= 0:
            self.loans.update_one({"loan_id": loan_id}, {"$set": {"remaining_balance": 0, "status": "paid"}})
            print("✅ Loan fully repaid!")
        else:
            self.loans.update_one({"loan_id": loan_id}, {"$set": {"remaining_balance": new_balance}})
            print(f"✅ Payment accepted. Remaining balance: ${new_balance:.2f}")

    def view_loans(self, acc_no):
        loans = self.loans.find({"account_number": acc_no})
        print(f"📄 Loans for account {acc_no}:")
        for loan in loans:
            print(f"Loan ID: {loan['loan_id']}, Balance: ${loan['remaining_balance']:.2f}, Status: {loan['status']}, Monthly: ${loan['monthly_payment']:.2f}")

    def log_transaction(self, acc_no, txn_type, amount, related_acc=None):
        self.transactions.insert_one({
            "account_number": acc_no,
            "type": txn_type,
            "amount": amount,
            "timestamp": datetime.now(),
            "related_account": related_acc
        })


def main():
    bank = BankSystem()

    while True:
        print("\n===== BANK SYSTEM MENU =====")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Check Balance")
        print("5. Transfer")
        print("6. Transaction History")
        print("7. Apply Interest")
        print("8. Apply for Loan")
        print("9. Repay Loan")
        print("10. View Loans")
        print("11. Exit")
        print("============================")

        choice = input("Enter your choice (1-11): ")

        if choice == '1':
            name = input("Account Holder Name: ")
            bal = float(input("Initial Balance: "))
            bank.create_account(name, bal)

        elif choice == '2':
            acc = input("Account Number: ")
            amt = float(input("Deposit Amount: "))
            bank.deposit(acc, amt)

        elif choice == '3':
            acc = input("Account Number: ")
            amt = float(input("Withdrawal Amount: "))
            bank.withdraw(acc, amt)

        elif choice == '4':
            acc = input("Account Number: ")
            bank.check_balance(acc)

        elif choice == '5':
            from_acc = input("From Account: ")
            to_acc = input("To Account: ")
            amt = float(input("Amount to Transfer: "))
            bank.transfer(from_acc, to_acc, amt)

        elif choice == '6':
            acc = input("Account Number: ")
            bank.show_transactions(acc)

        elif choice == '7':
            acc = input("Account Number (leave blank for all): ").strip()
            rate = float(input("Interest Rate (e.g., 0.02): "))
            bank.apply_interest(acc or None, rate)

        elif choice == '8':
            acc = input("Account Number: ")
            amt = float(input("Loan Amount: "))
            rate = float(input("Interest Rate (e.g., 0.05): "))
            duration = int(input("Duration in Months: "))
            bank.apply_loan(acc, amt, rate, duration)

        elif choice == '9':
            acc = input("Account Number: ")
            loan_id = input("Loan ID: ")
            payment = float(input("Payment Amount: "))
            bank.repay_loan(acc, loan_id, payment)

        elif choice == '10':
            acc = input("Account Number: ")
            bank.view_loans(acc)

        elif choice == '11':
            print("👋 Exiting. Thank you for using the bank system!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
