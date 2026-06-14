import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class FinanceManager:
    DATA_FILE = "expenses.json"
    
    def __init__(self):
        self.expenses: Dict[str, List[Dict]] = {}
        self.load_expenses()
    
    def load_expenses(self) -> None:
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r') as f:
                    self.expenses = json.load(f)
            else:
                self.expenses = {}
        except (json.JSONDecodeError, IOError) as e:
            self.expenses = {}
    
    def save_expenses(self) -> None:
        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump(self.expenses, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save expenses: {str(e)}")
    
    def add_expense(self, category: str, amount: float, description: str = "") -> str:
        try:
            if not category or not category.strip():
                return "ERROR: Category cannot be empty."
            
            category = category.strip().title()
            
            if amount <= 0:
                return "ERROR: Amount must be greater than zero."
            
            if category not in self.expenses:
                self.expenses[category] = []
            
            transaction = {
                "amount": round(amount, 2),
                "description": description.strip() if description else "",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.expenses[category].append(transaction)
            self.save_expenses()
            
            return f"✓ Added ${amount:.2f} to {category} on {transaction['timestamp']}"
        
        except ValueError:
            return "ERROR: Invalid amount. Please enter a valid number."
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def get_summary(self) -> str:
        if not self.expenses:
            return "No expenses recorded yet."
        
        totals = {}
        for category, transactions in self.expenses.items():
            totals[category] = sum(t["amount"] for t in transactions)
        
        grand_total = sum(totals.values())
        
        summary = "\n" + "="*60 + "\n"
        summary += "EXPENSE SUMMARY\n"
        summary += "="*60 + "\n\n"
        
        if not totals:
            return summary + "No categories with expenses.\n"
        
        max_total = max(totals.values())
        max_bar_length = 30
        
        for category in sorted(totals.keys()):
            amount = totals[category]
            percentage = (amount / grand_total) * 100
            bar_length = int((amount / max_total) * max_bar_length)
            bar = "█" * bar_length
            
            summary += f"{category:<15} ${amount:>8.2f} ({percentage:>5.1f}%) "
            summary += f"| {bar}\n"
        
        summary += "\n" + "-"*60 + "\n"
        summary += f"{'GRAND TOTAL':<15} ${grand_total:>8.2f}\n"
        summary += "-"*60 + "\n"
        
        return summary
    
    def get_history(self, limit: int = 20) -> str:
        if not self.expenses:
            return "No transaction history available."
        
        all_transactions = []
        for category, transactions in self.expenses.items():
            for transaction in transactions:
                all_transactions.append({
                    "category": category,
                    **transaction
                })
        
        all_transactions.sort(
            key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S"),
            reverse=True
        )
        
        history = "\n" + "="*60 + "\n"
        history += f"TRANSACTION HISTORY (Latest {min(limit, len(all_transactions))})\n"
        history += "="*60 + "\n\n"
        
        for i, trans in enumerate(all_transactions[:limit], 1):
            desc = f" - {trans['description']}" if trans['description'] else ""
            history += (f"{i:2}. [{trans['timestamp']}] {trans['category']:<15} "
                       f"${trans['amount']:>8.2f}{desc}\n")
        
        history += "\n" + "="*60 + "\n"
        
        return history
    
    def delete_category(self, category: str) -> str:
        category = category.strip().title()
        
        if category not in self.expenses:
            return f"ERROR: Category '{category}' not found."
        
        total = sum(t["amount"] for t in self.expenses[category])
        count = len(self.expenses[category])
        
        del self.expenses[category]
        self.save_expenses()
        
        return f"✓ Deleted {count} transaction(s) from {category} (Total: ${total:.2f})"
    
    def get_categories(self) -> List[str]:
        return sorted(self.expenses.keys())

class FinanceTrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("800x600")
        
        self.finance_manager = FinanceManager()
        self.state = "MENU"
        self.context = {}
        
        self._setup_colors()
        self._setup_ui()
        self._show_welcome()
    
    def _setup_colors(self) -> None:
        self.colors = {
            "bg": "#FAF8F5",
            "text": "#333333",
            "border": "#DCDCDC",
            "accent": "#8B7355"
        }
        self.root.configure(bg=self.colors["bg"])
    
    def _setup_ui(self) -> None:
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.output_text = ScrolledText(
            container,
            height=24,
            width=95,
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Consolas", 10),
            state=tk.DISABLED,
            wrap=tk.WORD,
            borderwidth=2,
            relief=tk.FLAT,
            insertbackground=self.colors["accent"]
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        input_frame = tk.Frame(container, bg=self.colors["bg"])
        input_frame.pack(fill=tk.X, pady=5)
        
        prompt_label = tk.Label(
            input_frame,
            text=">>> ",
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Consolas", 10)
        )
        prompt_label.pack(side=tk.LEFT)
        
        self.input_entry = tk.Entry(
            input_frame,
            bg="white",
            fg=self.colors["text"],
            font=("Consolas", 10),
            borderwidth=2,
            relief=tk.FLAT
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self._on_input_submit)
        self.input_entry.focus()
    
    def _show_welcome(self) -> None:
        self.state = "MENU"
        self._print_output("""
╔════════════════════════════════════════════════════════════════╗
║      💰 PERSONAL FINANCE TRACKER 💰                           ║
║                                                                ║
║ Track your expenses with style and simplicity                  ║
╚════════════════════════════════════════════════════════════════╝

""")
        self._show_menu()
    
    def _show_menu(self) -> None:
        menu_text = """
MAIN MENU - Select an option:

  1. Add Expense
  2. View Summary
  3. View History
  4. Delete Category
  5. Quit

Enter your choice (1-5): """
        self._print_output(menu_text)
    
    def _on_input_submit(self, event) -> None:
        user_input = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        
        if not user_input:
            return
        
        self._print_input(user_input)
        
        try:
            if self.state == "MENU":
                self._handle_menu_choice(user_input)
            elif self.state == "ADD_EXPENSE_CATEGORY":
                self._handle_add_category(user_input)
            elif self.state == "ADD_EXPENSE_AMOUNT":
                self._handle_add_amount(user_input)
            elif self.state == "ADD_EXPENSE_DESCRIPTION":
                self._handle_add_description(user_input)
            elif self.state == "DELETE_CATEGORY":
                self._handle_delete_category(user_input)
            elif self.state == "POST_EXPENSE_CHOICE":
                self._handle_post_expense_choice(user_input)
            elif self.state == "POST_VIEW_CHOICE":
                self._handle_post_view_choice(user_input)
            elif self.state == "POST_DELETE_CHOICE":
                self._handle_post_delete_choice(user_input)
            elif self.state == "CONTINUE_PROMPT":
                self._handle_continue()
        
        except Exception as e:
            self._print_output(f"\nERROR: {str(e)}\n")
            self._show_menu()
            self.state = "MENU"
    
    def _handle_menu_choice(self, choice: str) -> None:
        choice = choice.strip()
        
        if choice == "1":
            self._print_output("\n--- ADD EXPENSE ---\n")
            self._print_output("Enter category (e.g., Food, Transport, Entertainment): ")
            self.state = "ADD_EXPENSE_CATEGORY"
            self.context = {}
        
        elif choice == "2":
            self._print_output("\n" + self.finance_manager.get_summary())
            self._print_output("\n--- What would you like to do? ---\n")
            self._print_output("  1. Return to Main Menu\n")
            self._print_output("  2. Quit\n")
            self._print_output("\nEnter your choice (1 or 2): ")
            self.state = "POST_VIEW_CHOICE"
        
        elif choice == "3":
            self._print_output("\n" + self.finance_manager.get_history())
            self._print_output("\n--- What would you like to do? ---\n")
            self._print_output("  1. Return to Main Menu\n")
            self._print_output("  2. Quit\n")
            self._print_output("\nEnter your choice (1 or 2): ")
            self.state = "POST_VIEW_CHOICE"
        
        elif choice == "4":
            categories = self.finance_manager.get_categories()
            if not categories:
                self._print_output("No categories to delete.\n")
                self._show_menu()
                self.state = "MENU"
            else:
                self._print_output("\n--- DELETE CATEGORY ---\n")
                self._print_output("Available categories:\n")
                for i, cat in enumerate(categories, 1):
                    self._print_output(f"  {i}. {cat}\n")
                self._print_output("\nEnter category name to delete: ")
                self.state = "DELETE_CATEGORY"
        
        elif choice == "5":
            self._print_output("\nThank you for using Finance Tracker. Goodbye! 👋\n\n")
            self.root.after(500, self.root.quit)
        
        else:
            self._print_output("\nERROR: Invalid choice. Please select 1-5.\n")
            self._show_menu()
    
    def _handle_add_category(self, category: str) -> None:
        if not category or not category.strip():
            self._print_output("ERROR: Category cannot be empty.\n")
            self._print_output("Enter category: ")
            return
        
        self.context["category"] = category.strip()
        self._print_output("\nEnter amount ($): ")
        self.state = "ADD_EXPENSE_AMOUNT"
    
    def _handle_add_amount(self, amount_str: str) -> None:
        try:
            amount = float(amount_str.strip().replace("$", "").replace(",", ""))
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
            self.context["amount"] = amount
            self._print_output("\nEnter description (optional, press Enter to skip): ")
            self.state = "ADD_EXPENSE_DESCRIPTION"
        except ValueError as e:
            self._print_output(f"ERROR: Invalid amount. {str(e)}\n")
            self._print_output("Enter amount ($): ")
            self.state = "ADD_EXPENSE_AMOUNT"
    
    def _handle_add_description(self, description: str) -> None:
        result = self.finance_manager.add_expense(
            self.context["category"],
            self.context["amount"],
            description
        )
        self._print_output(f"\n{result}\n")
        self._print_output("\n--- What would you like to do? ---\n")
        self._print_output("  1. Add More Expenses\n")
        self._print_output("  2. Return to Main Menu\n")
        self._print_output("\nEnter your choice (1 or 2): ")
        self.state = "POST_EXPENSE_CHOICE"
    
    def _handle_delete_category(self, category: str) -> None:
        result = self.finance_manager.delete_category(category)
        self._print_output(f"\n{result}\n")
        self._print_output("\n--- What would you like to do? ---\n")
        self._print_output("  1. Return to Main Menu\n")
        self._print_output("  2. Quit\n")
        self._print_output("\nEnter your choice (1 or 2): ")
        self.state = "POST_DELETE_CHOICE"
    
    def _handle_post_expense_choice(self, choice: str) -> None:
        choice = choice.strip()
        
        if choice == "1":
            self._print_output("\n--- ADD EXPENSE ---\n")
            self._print_output("Enter category (e.g., Food, Transport, Entertainment): ")
            self.state = "ADD_EXPENSE_CATEGORY"
            self.context = {}
        elif choice == "2":
            self._print_output("\n")
            self._show_menu()
            self.state = "MENU"
        else:
            self._print_output("\nERROR: Invalid choice. Please select 1 or 2.\n")
            self._print_output("  1. Add More Expenses\n")
            self._print_output("  2. Return to Main Menu\n")
            self._print_output("\nEnter your choice (1 or 2): ")
    
    def _handle_post_view_choice(self, choice: str) -> None:
        choice = choice.strip()
        
        if choice == "1":
            self._print_output("\n")
            self._show_menu()
            self.state = "MENU"
        elif choice == "2":
            self._print_output("\nThank you for using Finance Tracker. Goodbye! 👋\n\n")
            self.root.after(500, self.root.quit)
        else:
            self._print_output("\nERROR: Invalid choice. Please select 1 or 2.\n")
            self._print_output("  1. Return to Main Menu\n")
            self._print_output("  2. Quit\n")
            self._print_output("\nEnter your choice (1 or 2): ")
    
    def _handle_post_delete_choice(self, choice: str) -> None:
        choice = choice.strip()
        
        if choice == "1":
            self._print_output("\n")
            self._show_menu()
            self.state = "MENU"
        elif choice == "2":
            self._print_output("\nThank you for using Finance Tracker. Goodbye! 👋\n\n")
            self.root.after(500, self.root.quit)
        else:
            self._print_output("\nERROR: Invalid choice. Please select 1 or 2.\n")
            self._print_output("  1. Return to Main Menu\n")
            self._print_output("  2. Quit\n")
            self._print_output("\nEnter your choice (1 or 2): ")
    
    def _handle_continue(self) -> None:
        self._show_menu()
        self.state = "MENU"
    
    def _print_output(self, text: str) -> None:
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def _print_input(self, text: str) -> None:
        self._print_output(f"{text}\n")

def main():
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()