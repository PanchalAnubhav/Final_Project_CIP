# Personal Finance Tracker
**Stanford Code in Place — Final Project**

A desktop application for tracking personal expenses by category, built with Python and Tkinter.

---

## Overview

Personal Finance Tracker is a GUI-based expense management tool that lets users log spending, visualize category breakdowns, and review transaction history — all from a clean, terminal-style interface. Data is saved locally as JSON, so records persist across sessions.

---

## Features

- **Add Expenses** — Log an amount under any category with an optional description
- **Visual Summary** — Bar chart rendered in-terminal showing spend per category with percentage breakdowns
- **Transaction History** — Chronological log of the 20 most recent entries
- **Delete Categories** — Remove an entire spending category and all its transactions
- **Persistent Storage** — All data saved to `expenses.json` automatically after every change

---

## How It Works

The project is structured around two classes:

### `FinanceManager` — Data Layer
Handles all business logic and file I/O:
- Loads and saves expense data to `expenses.json`
- Validates inputs (non-empty category, positive amount)
- Computes per-category totals and grand totals for the summary view
- Sorts transactions by timestamp for history display

### `FinanceTrackerApp` — UI Layer
Drives the Tkinter GUI using a **state machine** pattern:

| State | Description |
|---|---|
| `MENU` | Main menu — user picks an action (1–5) |
| `ADD_EXPENSE_CATEGORY` | Prompts for spending category |
| `ADD_EXPENSE_AMOUNT` | Prompts for dollar amount |
| `ADD_EXPENSE_DESCRIPTION` | Optional description before saving |
| `DELETE_CATEGORY` | Lists categories and awaits selection |
| `POST_*_CHOICE` | Post-action prompts (add more / return / quit) |

Each user input advances or resets the state, keeping the app flow predictable and easy to extend.

---

## Sample Interaction

```
>>> 1
--- ADD EXPENSE ---
Enter category: Food
Enter amount ($): 24.50
Enter description (optional): Lunch at Coupa Cafe

✓ Added $24.50 to Food on 2025-06-10 12:34:01
```

```
============================================================
EXPENSE SUMMARY
============================================================

Food            $  148.75 ( 42.3%) | ██████████████████████████████
Transport       $   89.00 ( 25.3%) | ██████████████████
Entertainment   $  113.50 ( 32.3%) | ███████████████████████████

------------------------------------------------------------
GRAND TOTAL     $  351.25
------------------------------------------------------------
```

---

## Technical Details

| Detail | Value |
|---|---|
| Language | Python 3 |
| GUI Framework | `tkinter` + `ScrolledText` |
| Data Storage | JSON (`expenses.json`) |
| Key Modules | `datetime`, `json`, `os`, `pathlib`, `typing` |
| Architecture | Two-class MVC-style split (data / UI) |
| Error Handling | Try/except on all I/O and user input paths |

---

## Running the Project

**Requirements:** Python 3.x (Tkinter is included in the standard library — no pip installs needed.)

```bash
python finance-tracker.py
```

The app window opens at 800×600. Type commands into the input field and press **Enter** to navigate.

---

## Concepts Applied

- **Classes and objects** with clear separation of responsibilities
- **File I/O** with JSON serialization and graceful error recovery
- **State machine** for managing multi-step user flows in a GUI
- **Type hints** (`Dict`, `List`, `Optional`) for code clarity
- **Input validation** with user-friendly error messages
- **Event-driven programming** via Tkinter's `.bind("<Return>", ...)` pattern

---

---

## Connect

Feel free to reach out or follow my work:

- 💼 **LinkedIn** — ([https://linkedin.com/in/anubhav-panchal-583378306](https://www.linkedin.com/in/anubhav-panchal-583378306/))
- 𝕏 **X (Twitter)** — ([https://x.com/_panchu_uu](https://x.com/_panchu_uu))

---

*Built for Stanford Code in Place · June 2026*
