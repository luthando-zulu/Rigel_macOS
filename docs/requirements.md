# RIGEL Business - Kilo Code Fix Instructions v2

**Version**: 2.0  
**Classification**: Confidential — Stella Lumen Internal Document  
**Date**: 2026  
**Modules**: 10 (Registration, Transact, Cash Book, Customers, Directors, Employees, Inventories, Assets, Projects, Adjustments)  
**Total Test Cases**: 116 (109 Pending, 5 Deferred, 2 Future)

---

## Document Overview

This document contains the complete Kilo Code fix instruction set for the v2 module suite of RIGEL Business. Each instruction block represents a single test case with expected behavior, current behavior, files to check, and required fixes.

### Status Legend
- **Pending** = Not yet tested (record Pass or Fail after testing)
- **Pass** = Confirmed working
- **Fail** = Fix required
- **Deferred** = CFS/future module (Cash Flow Statement not yet built)

### Critical Shared Fixes
1. **CCE Cumulative Update** (`rigel_core.py::update_cce()`): Shared across Suppliers, Inventories/Fixed Assets, Investments, Loans, Inventories, Assets, Directors (Loan to Director), Customers (Account Payment)
   - **Status**: Apply ONCE before addressing individual module Test IDs
   - **Reference**: RIGEL_Kilo_Code_Fix_Instructions.docx Section 1

---

## Module 1: Registration (18 Tests)

**Criticality**: FOUNDATION — All tests must pass before transactional module testing begins.  
**Source Files**: `registration/registration_handler.py`, `reporting/income_statement.py`, `reporting/balance_sheet.py`, `reporting/afs_notes.py`

### REG-001: Navigation to Registration Page
- **Expected**: Clicking 'Register Company' navigates to Registration page without errors
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`, `transact/navigation.py`
- **Fix**: Confirm button bound to correct route; verify page loads with all form fields

### REG-002: Grey Cell Editability
- **Expected**: All grey-shaded cells are editable and accept user input
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: Cell protection applied only to non-grey cells; grey cells unprotected

### REG-003: White Cell Protection
- **Expected**: All white-background cells locked; no editable state on click
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: Confirm white cells protected; no error dialog on click

### REG-004: Entity Name Propagation
- **Expected**: Entity name displayed consistently on all system pages; updates propagate
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`, `transact/navigation.py`
- **Fix**: Store name in shared app state; all headers read from this state; refresh pages on update

### REG-005: Update Last Year
- **Expected**: Populates prior-year opening balances into IS, BS, comparative columns
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`, `reporting/income_statement.py`, `reporting/balance_sheet.py`
- **Fix**: Read current year closing balances; write to Last Year column; don't overwrite current year

### REG-006: Category Dropdown
- **Expected**: Clicking category dropdown reveals correct sub-category options per RIGEL COA
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: Dropdown maps to RIGEL COA; each category reveals only valid sub-categories

### REG-007: Sub-Category & GL Code Auto-Fill
- **Expected**: Sub-category reveals correct accounts; GL code auto-fills on account selection
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: Dropdown driven by selected sub-category; GL auto-populate on selection

### REG-008: Post Transaction
- **Expected**: 'Post' adds transaction immediately to right-hand table with all columns
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: post() appends row; table refreshes immediately; data persists

### REG-009: Edit Transaction
- **Expected**: Selecting posting and clicking 'Edit' populates form; 'Post' updates (no duplicate)
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: 'Edit' loads record values; check if update vs new; update in place

### REG-010: Duplicate Prevention
- **Expected**: Posting duplicate (same category/subcategory/account) triggers alert; no duplicate created
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`
- **Fix**: Query existing records before post(); display error if found; abort post

### REG-011: Start Using Navigation & Validation
- **Expected**: 'Start Using' navigates to Main Menu; button only enabled after mandatory fields completed
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`, `transact/navigation.py`
- **Fix**: Button routes to Main Menu; disable until entity name and ≥1 account posted

### REG-012: Registration Button Navigation
- **Expected**: 'Registration' button on Main Menu navigates back to Registration page
- **Current**: Not yet tested
- **Files**: `transact/navigation.py`
- **Fix**: Confirm menu button routes correctly

### REG-013: Registration to IS Last Year
- **Expected**: All Revenue/Expenditure from Registration appear in IS 'Last Year' column on correct lines
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`, `reporting/income_statement.py`
- **Fix**: IS reads Last Year from registration data; each account on correct line; all present

### REG-014: Net Income to Retained Earnings
- **Expected**: Net Income After Tax flows automatically to BS Retained Earnings; no manual entry
- **Current**: Not yet tested
- **Files**: `reporting/income_statement.py`, `reporting/balance_sheet.py`
- **Fix**: IS NIAT cell reference links to BS Retained Earnings; automatic linkage

### REG-015: Registration to BS Last Year
- **Expected**: All Asset, Liability, Equity from Registration appear in BS 'Last Year' column
- **Current**: Not yet tested
- **Files**: `registration/registration_handler.py`, `reporting/balance_sheet.py`
- **Fix**: BS reads Last Year from registration; all balances on correct lines

### REG-016: BS Aggregation
- **Expected**: Assets/Liabilities aggregate correctly per RIGEL COA; Total Assets = Total Equity + Liabilities
- **Current**: Not yet tested
- **Files**: `reporting/balance_sheet.py`
- **Fix**: Verify aggregation logic; Retained Earnings = Total Equity minus Share Capital

### REG-017: BS Balance Check
- **Expected**: Total Assets = Total Equity and Liabilities; imbalance triggers critical error
- **Current**: Not yet tested
- **Files**: `reporting/balance_sheet.py`
- **Fix**: Balance check function; error dialog if imbalance; block proceed until balanced

### REG-018: AFS Review
- **Expected**: No errors in AFS after registration; no formula errors, blank fields, mismatches
- **Current**: Not yet tested
- **Files**: `reporting/afs_notes.py`, `reporting/income_statement.py`, `reporting/balance_sheet.py`
- **Fix**: Full AFS review post-registration; fix identified issues

---

## Module 2: Transact (4 Tests)

**Criticality**: HIGH — Navigation tests; must pass before module-specific testing.  
**Source Files**: `transact/navigation.py`, `reporting/dashboard.py`, `auth/session.py`

### TRN-001: Transact Button Navigation
- **Expected**: 'Transact' button from any screen navigates to Main Menu immediately
- **Status**: Pending
- **Files**: `transact/navigation.py`
- **Fix**: Confirm button bound to Main Menu route; no loading errors

### TRN-002: Left/Bottom Menu Navigation
- **Expected**: All Left/Bottom Menu buttons navigate to respective pages (CFS, Management Accounts)
- **Status**: Pending
- **Files**: `transact/navigation.py`
- **Fix**: Audit route bindings; confirm CFS and Management Accounts exist and accessible

### TRN-003: Dashboard Graph Refresh
- **Expected**: All graphs update correctly after transactions posted; no stale data; no manual refresh
- **Status**: Pending
- **Files**: `reporting/dashboard.py`
- **Fix**: Every post() calls refresh_dashboard(); graphs read live data, not cached

### TRN-004: Logout
- **Expected**: Logout exits cleanly; session cleared; user returned to login/splash screen
- **Status**: Pending
- **Files**: `transact/navigation.py`, `auth/session.py`
- **Fix**: Clear session state; route to login/splash

---

## Module 3: Cash Book (6 Tests)

**Criticality**: HIGH  
**Source Files**: `cashbook/cashbook_handler.py`, `rigel_core.py`, `reporting/trial_balance.py`, `reporting/balance_sheet.py`

### CB-001: Cell Protection
- **Expected**: Only blue-highlighted cells editable; all others locked
- **Status**: Pending
- **Files**: `cashbook/cashbook_handler.py`
- **Fix**: Blue unprotected; others locked silently

### CB-002: Opening Bank Balance Impact
- **Expected**: Opening Bank Balance entry increases BS Cash & Cash Equivalents; Retained Earnings adjusted
- **Status**: Pending
- **Files**: `cashbook/cashbook_handler.py`, `reporting/balance_sheet.py`
- **Fix**: Dr Cash; Cr Retained Earnings; BS updates immediately; TB balances

### CB-003: Auto-Populate Opening Balance (Enhancement)
- **Expected**: Opening Bank Balance auto-populated from Registration Last Year CCE balance
- **Status**: Pending — Enhancement
- **Files**: `cashbook/cashbook_handler.py`, `registration/registration_handler.py`
- **Fix**: On page load: read Registration Last Year CCE; pre-populate field; allow override

### CB-004: Opening Balance Carry-Forward
- **Expected**: Last Year closing balances from Registration become Current Year opening balances in BS
- **Status**: Pending
- **Files**: `registration/registration_handler.py`, `reporting/balance_sheet.py`
- **Fix**: BS 'Opening Balance' column reads from Registration Last Year; automatic linkage

### CB-005: Document Number Field
- **Expected**: Evaluate Document Number field requirement; deactivate/hide if not required
- **Status**: Pending — Design Decision
- **Files**: `cashbook/cashbook_handler.py`
- **Fix**: Discuss with lead: required or hide? (don't delete)

### CB-006: Full Posting Chain
- **Expected**: Cash Book entries post to GL (debit/credit), TB, BS, all reports correctly
- **Status**: Pending
- **Files**: `cashbook/cashbook_handler.py`, `rigel_core.py`, `reporting/trial_balance.py`, `reporting/balance_sheet.py`
- **Fix**: Trace sample receipt/payment through all four destinations

---

## Module 4: Customers (14 Tests, 1 Deferred)

**Criticality**: HIGH  
**Source Files**: `customers/customer_handler.py`, `customers/masterfile.py`, `rigel_core.py`, `reporting/*.py`

### CUS-001: Cell Protection
- **Expected**: Grey-shaded cells editable; all others locked
- **Status**: Pending
- **Fix**: Grey editable; others locked silently

### CUS-002: Account Payment Option
- **Expected**: 'Account Payment' available in Nature of Transaction dropdown; enables relevant fields
- **Status**: Pending
- **Files**: `customers/customer_handler.py`
- **Fix**: Confirm in dropdown; enables Customer, Amount, Date, Description

### CUS-003: Account Payment Posting
- **Expected**: 'Post Transaction' posts to View Transactions with all columns: Date, Code, Customer, Description, Amount, Category
- **Status**: Pending
- **Fix**: post() writes all columns; appears immediately

### CUS-004: Unique Transaction Code
- **Expected**: Auto-generated unique code (e.g., CUS-2026-0001); no duplicates
- **Status**: Pending
- **Fix**: Unique code generation + uniqueness check

### CUS-005: Account Payment TB Posting
- **Expected**: TB posts: Dr Cash (increase); Cr Trade Receivables (decrease); TB balances
- **Status**: Pending
- **Files**: `customers/customer_handler.py`, `rigel_core.py`, `reporting/trial_balance.py`
- **Fix**: Both legs post; TB balances

### CUS-006: Account Payment BS Posting
- **Expected**: BS: Cash increases; Trade Receivables decrease; net WC effect zero
- **Status**: Pending
- **Files**: `reporting/balance_sheet.py`
- **Fix**: BS updates correctly after payment posting

### CUS-007: CFS Working Capital (Deferred)
- **Expected**: Trade Receivables movement from Account Payments in CFS Operating Activities (working capital note)
- **Status**: DEFERRED — CFS not yet built
- **Fix**: None now; include when CFS built

### CUS-008: Account Payment GL
- **Expected**: All customer payments post to GL in correct debit/credit columns
- **Status**: Pending
- **Files**: `rigel_core.py`
- **Fix**: Trace sample to GL; Dr Cash, Cr Trade Receivables

### CUS-009: Deposit to Masterfile
- **Expected**: Customer deposits post to Masterfile against correct customer, month; minus effect on outstanding balance
- **Status**: Pending
- **Files**: `customers/masterfile.py`
- **Fix**: Deposit reduces outstanding balance in correct month column

### CUS-010: Receive Deposit Option
- **Expected**: 'Receive Deposit' available in Nature of Transaction dropdown
- **Status**: Pending
- **Files**: `customers/customer_handler.py`
- **Fix**: Confirm in dropdown; enables deposit fields

### CUS-011: Deposit Posting
- **Expected**: Deposit posts to: View Transactions, TB (Dr Cash / Cr Customer Deposits Received Liability), BS (Cash/Liability increase)
- **Status**: Pending
- **Files**: `customers/customer_handler.py`, `rigel_core.py`
- **Fix**: Confirm all three; Trade Receivables NOT affected

### CUS-012: Refund Deposit Option
- **Expected**: 'Refund Deposit' available in Nature of Transaction dropdown
- **Status**: Pending
- **Fix**: Confirm in dropdown; enables refund fields

### CUS-013: Refund Posting
- **Expected**: Refund posts to: View Transactions, TB (Dr Liability / Cr Cash), BS (Cash/Liability decrease)
- **Status**: Pending
- **Files**: `customers/customer_handler.py`, `rigel_core.py`
- **Fix**: Reverses deposit correctly

### CUS-014: Dashboard Refresh
- **Expected**: Customer-related graphs and KPIs update after each transaction; no manual refresh
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `customers/customer_handler.py`
- **Fix**: refresh_dashboard() called at end of all customer post() methods

---

## Module 5: Directors (17 Tests, 2 Deferred)

**Criticality**: HIGH  
**Source Files**: `directors/director_handler.py`, `directors/masterfile.py`, `rigel_core.py`, `reporting/*.py`  
**Note**: Handles Director Dividends (Pay Dividend) + Director Loans (Loan by Director / Loan to Director). Loan repayments in Loans module (v1).

### DIR-001: Cell Protection
- **Expected**: Grey-shaded cells editable; all others locked
- **Status**: Pending
- **Fix**: Grey editable; others locked silently

### DIR-002: Pay Dividend Option
- **Expected**: 'Pay Dividend' available in Nature of Transaction dropdown
- **Status**: Pending
- **Fix**: Confirm in dropdown; enables dividend fields

### DIR-003: Dividend Posting
- **Expected**: Dividends post to View Transactions with columns: Date, Code, Director, Gross Dividend, Dividends Tax (20%), Net Dividend (80%), Category
- **Status**: Pending
- **Files**: `directors/director_handler.py`
- **Fix**: post() splits gross into 80% net + 20% tax; records both

### DIR-004: Unique Transaction Code
- **Expected**: Auto-generated unique code (e.g., DIR-2026-0001); no duplicates
- **Status**: Pending
- **Fix**: Unique code generation + check

### DIR-005: Dividend TB Posting
- **Expected**: TB: Dr Dividends Declared (80% gross); Dr Dividends Tax Payable (20%); Cr Cash (100%); TB balances
- **Status**: Pending
- **Files**: `directors/director_handler.py`, `rigel_core.py`, `reporting/trial_balance.py`
- **Fix**: Three legs post; Gross = Net + Tax (80% + 20% = 100%); TB balances

### DIR-006: Dividend IS Posting
- **Expected**: Dividends Declared posts to IS (or Statement of Changes in Equity per RIGEL design)
- **Status**: Pending
- **Files**: `directors/director_handler.py`, `reporting/income_statement.py`
- **Fix**: Appears in correct IS section; confirm RIGEL's design choice

### DIR-007: Dividend BS Impact
- **Expected**: BS: Cash decreases (gross); Retained Earnings decreases (Dividends Declared); Dividends Tax Payable decreases when paid
- **Status**: Pending
- **Files**: `reporting/balance_sheet.py`
- **Fix**: All three effects reflect correctly

### DIR-008: Dividend AFS Tax Note
- **Expected**: Dividends Tax posts correctly to AFS Note 6 (Taxation); shows gross/withholding/net split
- **Status**: Pending
- **Files**: `reporting/afs_notes.py`
- **Fix**: Note 6 reads Dividends Tax Payable; displays correct split

### DIR-009: Dividend CFS (Deferred)
- **Expected**: Dividend cash outflow in CFS Financing Activities
- **Status**: DEFERRED — CFS not yet built
- **Fix**: None now; include when CFS built

### DIR-010: Dividend GL
- **Expected**: All dividend transactions post to GL in correct debit/credit columns
- **Status**: Pending
- **Files**: `rigel_core.py`
- **Fix**: Trace sample to GL

### DIR-011: Loan by Director
- **Expected**: 'Loan by Director' posts: Dr Cash; Cr Loans from Directors (Current/Non-Current Liability); View Transactions, TB, BS update
- **Status**: Pending
- **Files**: `directors/director_handler.py`, `rigel_core.py`
- **Fix**: Correct double-entry; loan classification applied; all three update

### DIR-012: Loan by Director AFS Note
- **Expected**: Loan by Director posts to AFS Note 2 (Loans from Directors) with balance, interest rate, terms
- **Status**: Pending
- **Files**: `reporting/afs_notes.py`
- **Fix**: Note 2 reads GL account; displays all details

### DIR-013: Loan Receipt CFS (Deferred)
- **Expected**: Loan receipt from Director in CFS Financing Activities (cash inflow)
- **Status**: DEFERRED — CFS not yet built
- **Fix**: None now

### DIR-014: Loan to Director
- **Expected**: 'Loan to Director' posts: Dr Loans to Directors (Current/Non-Current Asset); Cr Cash; View Transactions, TB, BS update
- **Status**: Pending
- **Files**: `directors/director_handler.py`, `rigel_core.py`
- **Fix**: Correct double-entry; Asset classification; CCE decreases cumulatively (shared fix)

### DIR-015: Loan to Director AFS Note
- **Expected**: Loan to Director posts to AFS Note 2 (Loans to Directors) Asset side with balance, interest, terms
- **Status**: Pending
- **Files**: `reporting/afs_notes.py`
- **Fix**: Separate Loans to Directors section; all details display

### DIR-016: Loan Masterfile
- **Expected**: Loan transactions post to Director Masterfile; correct director, month; plus/minus effect on outstanding balance
- **Status**: Pending
- **Files**: `directors/masterfile.py`
- **Fix**: Masterfile tracks balances per director per month; Loan by = plus; Loan to = minus

### DIR-017: Dashboard Refresh
- **Expected**: Director-related graphs/KPIs update after each transaction; no manual refresh
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `directors/director_handler.py`
- **Fix**: refresh_dashboard() called at end of all director post() methods

---

## Module 6: Employees (6 Tests)

**Criticality**: HIGH  
**Source Files**: `employees/payroll_handler.py`, `employees/masterfile.py`, `rigel_core.py`, `reporting/*.py`

### EMP-001: Cell Protection
- **Expected**: Grey-shaded cells editable; all others locked
- **Status**: Pending
- **Fix**: Grey editable; others locked silently

### EMP-002: Salary Posting (Full Chain)
- **Expected**: Salaries post to: View Transactions (all columns), TB (Dr Salaries & Wages / Cr Cash net / Cr Statutory Liabilities), IS, BS, GL
- **Status**: Pending
- **Files**: `employees/payroll_handler.py`, `rigel_core.py`, `reporting/*.py`
- **Fix**: Gross split: net + PAYE + UIF + SDL; all legs fire; IS reflects gross

### EMP-003: Statutory Deductions
- **Expected**: PAYE, UIF, SDL calculated correctly from gross; post to correct liability accounts; Net Pay = Gross - all deductions
- **Status**: Pending
- **Files**: `employees/payroll_handler.py`
- **Fix**: PAYE uses correct SARS tables; UIF (1% emp + 1% emp); SDL (1%); all liabilities in BS

### EMP-004: Employee Masterfile
- **Expected**: Employee records created with: name, ID, tax number, bank account, salary, tax status; link to payroll transactions
- **Status**: Pending
- **Files**: `employees/masterfile.py`
- **Fix**: All fields present; mandatory validation; code links to transactions

### EMP-005: Full Payroll Cycle
- **Expected**: Complete payroll (input → deduction calculation → journal entries) updates IS, BS, TB, GL accurately
- **Status**: Pending
- **Files**: `employees/payroll_handler.py`, `reporting/*.py`
- **Fix**: End-to-end cycle; all statements reflect correct figures

### EMP-006: Dashboard Refresh
- **Expected**: Employee-related graphs (payroll summary, headcount, cost breakdown) update after posting
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `employees/payroll_handler.py`
- **Fix**: refresh_dashboard() called at end of payroll post() methods

---

## Module 7: Inventories (9 Tests, 1 Deferred)

**Criticality**: HIGH  
**Source Files**: `inventories/inventory_handler.py`, `inventories/masterfile.py`, `rigel_core.py`, `reporting/*.py`  
**Note**: INVMOD- prefix (vs INV- for Suppliers module v1)

### INVMOD-001: Cell Protection & Categories
- **Expected**: Grey cells editable; all categories (Stock Receipt, Stock Issue, Adjustment) selectable
- **Status**: Pending
- **Fix**: Cell protection confirmed; all three types selectable

### INVMOD-002: Stock Receipt Posting
- **Expected**: Receipt posts: Dr Inventory (net cost); Cr Cash OR Cr Trade Payables; Dr VAT Input (if applicable); TB/BS update
- **Status**: Pending
- **Files**: `inventories/inventory_handler.py`, `rigel_core.py`
- **Fix**: All legs fire; CCE/Trade Payables correct per payment method

### INVMOD-003: COGS Posting
- **Expected**: Inventory issued/sold: Dr COGS (IS expense); Cr Inventory (BS decreases); IS COGS updates; Inventory balance decreases
- **Status**: Pending
- **Files**: `inventories/inventory_handler.py`, `reporting/income_statement.py`
- **Fix**: COGS = Qty × Avg Cost (or FIFO/LIFO per design); both legs post; IS updates

### INVMOD-004: Stock Adjustment
- **Expected**: Adjustments (write-offs, count variances) post: Dr Write-Off/Adjustment; Cr Inventory; appears in View Transactions/GL
- **Status**: Pending
- **Files**: `inventories/inventory_handler.py`
- **Fix**: Adjustment logic; write-offs reduce Inventory & create IS expense

### INVMOD-005: Inventory Masterfile
- **Expected**: Items created with: code, description, cost price, selling price, QOH, location, UOM; link to transactions
- **Status**: Pending
- **Files**: `inventories/masterfile.py`
- **Fix**: All fields present; mandatory validation; code unique

### INVMOD-006: Inventory TB/BS Accuracy
- **Expected**: Inventory balance accurately reflected in TB/BS; Opening + Receipts - Issues - Write-Offs = Closing
- **Status**: Pending
- **Files**: `reporting/trial_balance.py`, `reporting/balance_sheet.py`
- **Fix**: After receipts/issues, verify closing matches expected calculation

### INVMOD-007: COGS in IS
- **Expected**: COGS appears in IS when sold; receipts alone do NOT appear in IS (capitalized to BS)
- **Status**: Pending
- **Files**: `reporting/income_statement.py`
- **Fix**: Only issues trigger COGS; receipts don't affect IS

### INVMOD-008: CFS Working Capital (Deferred)
- **Expected**: Inventory movements in CFS Operating Activities (working capital note)
- **Status**: DEFERRED — CFS not yet built
- **Fix**: None now; include when CFS built

### INVMOD-009: Dashboard Refresh
- **Expected**: Stock levels, turnover, WC Dashboard graphs update after each transaction
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `inventories/inventory_handler.py`
- **Fix**: refresh_dashboard() and refresh_wc_dashboard() called at end of inventory post()

---

## Module 8: Assets (11 Tests)

**Criticality**: HIGH — CCE cumulative fix required for AST-004  
**Source Files**: `assets/asset_handler.py`, `rigel_core.py`, `reporting/afs_notes.py`, `reporting/balance_sheet.py`

### AST-001: Cell Protection
- **Expected**: Grey-shaded cells editable; all others locked
- **Status**: Pending
- **Fix**: Grey editable; others locked silently

### AST-002: Asset Classes
- **Expected**: All 5 Asset Classes (Buildings, Vehicles, Furniture, Computer Equipment, Fittings) available; each posts to correct GL account
- **Status**: Pending
- **Files**: `assets/asset_handler.py`
- **Fix**: All five in dropdown; each maps to own GL account

### AST-003: Unique Transaction Code
- **Expected**: Auto-generated unique code (e.g., AST-2026-0001); no duplicates
- **Status**: Pending
- **Fix**: Unique code generation + check

### AST-004: Asset Posting (CCE Cumulative Fix Required)
- **Expected**: All Asset Classes/VAT post: Dr PPE (net per class); Dr VAT Input; Cr Cash (cumulative); TB balances
- **Status**: Pending — **REQUIRES SHARED CCE FIX FIRST**
- **Files**: `assets/asset_handler.py`, `rigel_core.py`
- **Fix**: All three legs post; CCE CUMULATIVE (shared fix); each class own PPE account

### AST-005: AFS Note 1 (PPE)
- **Expected**: Each Asset Class posts to AFS Note 1 (PPE) cost row; VAT excluded (net cost only)
- **Status**: Pending
- **Files**: `reporting/afs_notes.py`
- **Fix**: Note 1 has row per class; Cost = net only; GL provides net correctly

### AST-006: AFS Note 6 (VAT)
- **Expected**: VAT Input posts to AFS Note 6 (VAT/SARS); traceable from transaction; sum matches TB
- **Status**: Pending
- **Files**: `reporting/afs_notes.py`
- **Fix**: Note 6 reads VAT Input; sum of all asset VAT = TB balance

### AST-007: CFS Investing Activities
- **Expected**: Asset purchases post to CFS Additions line (investing outflow); gross amount including VAT
- **Status**: Pending — Pending CFS build
- **Files**: `reporting/cash_flow_statement.py` (to be created)
- **Fix**: When CFS built: classify as investing outflows; use gross amount

### AST-008: Asset GL Posting
- **Expected**: All asset transactions post to GL in correct debit/credit columns
- **Status**: Pending
- **Files**: `rigel_core.py`
- **Fix**: Trace sample through GL; Dr PPE (class), Dr VAT Input, Cr Cash all appear

### AST-009: Asset Disposal
- **Expected**: Disposal removes asset at carrying value; proceeds Dr Cash; Gain/Loss to IS; all update
- **Status**: Pending
- **Files**: `assets/asset_handler.py`, `rigel_core.py`, `reporting/income_statement.py`
- **Fix**: Remove at carrying value (not cost); Gain/Loss = Proceeds - Carrying; IS updates; BS removes asset

### AST-010: CFS Disposal Proceeds
- **Expected**: Disposal proceeds in CFS Investing Activities (inflow); Note 1 Disposals column updated
- **Status**: Pending — Pending CFS build
- **Files**: `reporting/afs_notes.py`, `reporting/cash_flow_statement.py`
- **Fix**: Note 1 Disposals column populated; when CFS built: proceeds as investing inflows

### AST-011: Dashboard Refresh
- **Expected**: Asset-related graphs (capex trend, class breakdown, NBV over time) update after each transaction
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `assets/asset_handler.py`
- **Fix**: refresh_dashboard() called at end of asset post() methods

---

## Module 9: Projects (5 Tests)

**Criticality**: MEDIUM — Cross-module feature requiring changes to Expenses, Customers, Assets  
**Source Files**: `projects/project_handler.py`, `reporting/dashboard.py`

### PRJ-001: Project Masterfile
- **Expected**: Projects created with: code, name, budget, status (Active/Inactive); Masterfile displays all with status/budget
- **Status**: Pending
- **Files**: `projects/project_handler.py`
- **Fix**: All fields present; mandatory validation; code unique; Masterfile displays

### PRJ-002: Project Allocation in Transactions
- **Expected**: Expenses, revenue, asset purchases allocated to specific projects at posting; Project Code dropdown appears
- **Status**: Pending
- **Files**: `projects/project_handler.py`, `suppliers/expense_handler.py`, `customers/customer_handler.py`, `assets/asset_handler.py`
- **Fix**: Add Project Code dropdown to all relevant forms; save allocation; optional field

### PRJ-003: Project Reporting
- **Expected**: Project-wise P&L, Budget vs Actual, WIP visible/accurate; figures reconcile to main statements
- **Status**: Pending
- **Files**: `projects/project_handler.py`, `reporting/dashboard.py`
- **Fix**: P&L reads allocated transactions; Budget vs Actual accurate; WIP = costs for incomplete projects; reconciles to IS

### PRJ-004: Project Dimension (GL Roll-Up)
- **Expected**: Project-allocated transactions roll up to GL, IS, BS correctly; project coding is additional dimension
- **Status**: Pending
- **Files**: `projects/project_handler.py`, `rigel_core.py`
- **Fix**: Project-allocated transactions still post normally to GL/TB/IS/BS; project code is tag/dimension only

### PRJ-005: Project Dashboard
- **Expected**: Project graphs (spend vs budget, profitability) update after each project-allocated transaction
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `projects/project_handler.py`
- **Fix**: Dashboard refresh called after project-allocated postings

---

## Module 10: Adjustments (6 Tests)

**Criticality**: HIGH  
**Source Files**: `adjustments/adjustment_handler.py`, `audit/audit_trail.py`, `rigel_core.py`, `reporting/*.py`  
**Note**: ADJ-005 requires audit/audit_trail.py build (ref SMF-008 v1 instructions)

### ADJ-001: Cell Protection & Entry Fields
- **Expected**: Grey cells editable; 'Journal Adjustment' category available; both debit and credit fields present
- **Status**: Pending
- **Files**: `adjustments/adjustment_handler.py`
- **Fix**: Cell protection; category in dropdown; both Dr/Cr fields editable

### ADJ-002: Journal Entry Posting & Balance Check
- **Expected**: Entries post to View Transactions, GL, TB; must balance (Dr total = Cr total) before posting
- **Status**: Pending
- **Files**: `adjustments/adjustment_handler.py`, `rigel_core.py`
- **Fix**: Balance check before post(); if imbalance: display error, block post

### ADJ-003: Adjustment Impact on Statements
- **Expected**: Adjustments correctly affect IS, BS, Retained Earnings based on accounts debited/credited
- **Status**: Pending
- **Files**: `adjustments/adjustment_handler.py`, `reporting/income_statement.py`, `reporting/balance_sheet.py`
- **Fix**: Income/expense adjustments flow through IS to Retained Earnings; BS-only adjustments don't affect IS

### ADJ-004: Reversing Journals
- **Expected**: If supported: reversal posts in next period without duplication; original/reversal linked; tracing possible
- **Status**: Pending — Design Decision
- **Files**: `adjustments/adjustment_handler.py`
- **Fix**: Determine if in scope; if yes: reversal = exact opposite; linked via field; no duplication

### ADJ-005: Audit Trail Logging
- **Expected**: All adjustments logged in Audit Trail: user, date/time, reason, accounts, amounts, before/after values
- **Status**: Pending
- **Files**: `adjustments/adjustment_handler.py`, `audit/audit_trail.py`
- **Fix**: audit_trail.log() called for every adjustment; reason mandatory; before/after captured for all balances

### ADJ-006: Dashboard Refresh
- **Expected**: Adjustments reflected in dashboards/graphs after posting; no pre-adjustment figures after post
- **Status**: Pending
- **Files**: `reporting/dashboard.py`, `adjustments/adjustment_handler.py`
- **Fix**: refresh_dashboard() called at end of adjustment post() methods

---

## Implementation Checklist by Phase

### Phase 1: Foundation (Must Complete First)
- [ ] Registration Module (18 tests) - ALL MUST PASS
- [ ] Transact Module (4 tests) - ALL MUST PASS

### Phase 2: Core Transactions
- [ ] Cash Book Module (6 tests)
- [ ] Customers Module (13 tests - excl CUS-007)
- [ ] Directors Module (15 tests - excl DIR-009, DIR-013)
- [ ] Employees Module (6 tests)

### Phase 3: Advanced Features
- [ ] Inventories Module (8 tests - excl INVMOD-008)
- [ ] Assets Module (10 tests - excl AST-007, AST-010)
- [ ] Projects Module (5 tests)
- [ ] Adjustments Module (6 tests)

### Phase 4: Deferred (CFS-dependent)
- [ ] CUS-007, DIR-009, DIR-013, INVMOD-008, AST-007, AST-010

---

## Critical Shared Fixes

### CCE Cumulative Update (`rigel_core.py::update_cce()`)
**Modules Affected**: Suppliers, Inventories, Investments, Loans, Assets, Directors (Loan to Director), Customers (Account Payment)  
**Impact**: Cash & Cash Equivalents must update cumulatively across all modules  
**Status**: Apply ONCE before individual module Test IDs  
**Ref**: RIGEL_Kilo_Code_Fix_Instructions.docx Section 1

---

## Testing Strategy

1. **Manual Testing**: Run each test case manually before marking Pass/Fail
2. **Trace Testing**: For complex postings, trace through GL → TB → IS → BS → AFS
3. **Reconciliation**: End balances must reconcile to manual calculations
4. **Dashboard Verification**: Graphs update in real-time after each transaction
5. **Edge Cases**: Test duplicates, reversals, boundary conditions

---

## Repository Information

**Repository**: To be specified for push  
**Branch**: To be confirmed  
**Commit Message Format**: `[Module-ID] Description - Test IDs passed (X/Y)`

---

*End of Requirements Document*
