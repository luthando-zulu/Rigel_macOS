# RIGEL Business — Implementation Plan

**Document**: Kilo Code Fix Instructions v2 — Complete Module Suite  
**Status**: Ready for Implementation  
**Date Created**: 2026-05-06  
**Total Tasks**: 116 test cases across 10 modules

---

## Overview

This document provides a detailed implementation roadmap for executing the Kilo Code Fix Instructions v2. The requirements have been structured, prioritized, and are ready for systematic implementation.

### Quick Reference

| Module | Tests | Priority | Status |
|--------|-------|----------|--------|
| Registration | 18 | P0 (Foundation) | Ready |
| Transact | 4 | P0 (Foundation) | Ready |
| Cash Book | 6 | P1 (Core) | Ready |
| Customers | 14 | P1 (Core) | Ready |
| Directors | 17 | P1 (Core) | Ready |
| Employees | 6 | P1 (Core) | Ready |
| Inventories | 9 | P2 (Advanced) | Ready |
| Assets | 11 | P2 (Advanced) | Ready |
| Projects | 5 | P2 (Advanced) | Ready |
| Adjustments | 6 | P2 (Advanced) | Ready |
| **TOTAL** | **96** | — | — |
| *Deferred (CFS)* | *5* | — | Blocked |

---

## Implementation Phases

### Phase 0: Pre-Implementation (Completed)
- [x] Reviewed complete requirements document
- [x] Created `docs/requirements.md` with structured test cases
- [x] Analyzed project structure and existing codebase
- [x] Identified shared fixes and cross-module dependencies

### Phase 1: Foundation (Blocking Dependency)
**Duration**: Est. 4-6 days  
**Deliverables**: REG-001 to REG-018, TRN-001 to TRN-004

**Must be 100% complete before Phase 2 begins.**

1. **Registration Module (REG-001–REG-018)**
   - Navigation and page routing
   - Cell protection and form validation
   - Entity name state management
   - Chart of Accounts integration
   - Post/Edit/Delete transaction logic
   - Duplicate prevention
   - Opening balance flow to Income Statement
   - Opening balance flow to Balance Sheet
   - Balance Sheet balance validation
   - AFS integration and cross-references

2. **Transact Module (TRN-001–TRN-004)**
   - Navigation routing from any screen
   - Left/Bottom Menu navigation
   - Dashboard graph refresh logic
   - Logout session management

### Phase 2: Core Transactions (Parallel Development)
**Duration**: Est. 10-14 days  
**Deliverables**: CB-001–CB-006, CUS-001–CUS-014, DIR-001–DIR-017, EMP-001–EMP-006

**Prerequisite**: Phase 1 (100% complete)

**Critical Shared Fix Required**: `rigel_core.py::update_cce()`
- Apply ONCE at start of Phase 2
- Affects: Cash Book, Customers (Account Payment), Directors (Loan to Director), Assets
- Must handle cumulative Cash & Cash Equivalents updates

Modules can be implemented in parallel:
1. **Cash Book (CB-001–CB-006)**
   - Opening bank balance entry
   - CCE impact on BS
   - Opening balance carry-forward
   - Full posting chain (GL → TB → BS → Reports)

2. **Customers (CUS-001–CUS-014)**
   - Account payment transactions
   - Customer deposit/refund handling
   - Trade Receivables updates
   - Masterfile integration
   - Dashboard updates

3. **Directors (DIR-001–DIR-017)**
   - Dividend posting (80/20 split)
   - Dividend tax calculation and liability
   - Director loan (by/to) accounting
   - Masterfile tracking
   - AFS Note 2 integration

4. **Employees (EMP-001–EMP-006)**
   - Payroll processing
   - Statutory deduction calculation (PAYE, UIF, SDL)
   - Masterfile creation
   - End-to-end payroll cycle
   - Dashboard updates

### Phase 3: Advanced Features (Parallel Development)
**Duration**: Est. 12-16 days  
**Deliverables**: INVMOD-001–INVMOD-009, AST-001–AST-011, PRJ-001–PRJ-005, ADJ-001–ADJ-006

**Prerequisite**: Phase 2 (100% complete)

**Note**: AST-004 requires CCE cumulative fix (applied in Phase 2)

Modules can be implemented in parallel:
1. **Inventories (INVMOD-001–INVMOD-009)**
   - Stock receipt/issue/adjustment posting
   - COGS calculation (average cost/FIFO/LIFO)
   - Inventory masterfile
   - TB/BS accuracy
   - Dashboard updates

2. **Assets (AST-001–AST-011)**
   - 5 asset classes (Buildings, Vehicles, Furniture, Equipment, Fittings)
   - Unique asset codes
   - PPE posting (net cost per class)
   - VAT Input handling
   - AFS Note 1 integration
   - Asset disposal (gain/loss)
   - Dashboard updates

3. **Projects (PRJ-001–PRJ-005)**
   - Project masterfile
   - Project allocation to transactions (Expenses, Customers, Assets)
   - Project-wise P&L and Budget vs Actual
   - Project dimension integration (GL roll-up)
   - Dashboard updates
   - **Note**: Requires modifications to Expenses, Customers, Assets forms

4. **Adjustments (ADJ-001–ADJ-006)**
   - Journal entry posting with balance check
   - Impact on IS/BS/Retained Earnings
   - Reversing journal support (optional)
   - Audit trail logging
   - Dashboard updates

### Phase 4: Deferred (CFS-Dependent)
**Duration**: After CFS module implementation  
**Deliverables**: CUS-007, DIR-009, DIR-013, INVMOD-008, AST-007, AST-010

**Note**: These tests require Cash Flow Statement module (not yet built)
- CUS-007: Trade Receivables movement in CFS Operating Activities
- DIR-009, DIR-013: Dividend/Loan cash flows in CFS Financing Activities
- INVMOD-008: Inventory movements in CFS Operating Activities (working capital)
- AST-007, AST-010: Asset purchases/disposals in CFS Investing Activities

---

## Critical Dependencies & Shared Fixes

### Shared Fix 1: CCE Cumulative Update
**File**: `rigel_core.py::update_cce()`  
**Scope**: Core accounting engine update required for multiple modules

**Affected Modules**:
- Suppliers (prior - v1)
- Customers (Account Payment) - CUS-005, CUS-006
- Directors (Loan to Director) - DIR-014
- Assets - AST-004
- Inventories (prior - v1)
- Investments, Loans (prior - v1)

**Implementation Note**: Apply once in Phase 2, before individual module test IDs

### Dependency Chain
```
Phase 1 (Foundation) ✓
  ├── REG-001–REG-018
  └── TRN-001–TRN-004
    ↓
Phase 2 (Core) — Parallel Implementation
  ├── CB-001–CB-006 [Requires: CCE fix]
  ├── CUS-001–CUS-014 [Requires: CCE fix for CUS-005, CUS-006]
  ├── DIR-001–DIR-017 [Requires: CCE fix for DIR-014]
  └── EMP-001–EMP-006
    ↓
Phase 3 (Advanced) — Parallel Implementation
  ├── INVMOD-001–INVMOD-009
  ├── AST-001–AST-011 [Requires: CCE fix from Phase 2]
  ├── PRJ-001–PRJ-005 [Requires: Expenses, Customers, Assets modules]
  └── ADJ-001–ADJ-006
    ↓
Phase 4 (Deferred) — After CFS module
  └── CUS-007, DIR-009, DIR-013, INVMOD-008, AST-007, AST-010
```

---

## Testing Strategy by Phase

### Phase 1 Testing
1. **Manual Test Execution**: Each test case manually before marking Pass/Fail
2. **Form Validation**: All fields, dropdowns, cell protection
3. **Navigation**: Button routing, page loading
4. **Data Integrity**: No errors in logs, proper error handling

### Phase 2 Testing
1. **Transaction Posting**: GL → TB → IS → BS → AFS chain
2. **Reconciliation**: Manual calculation vs system balance
3. **Account Balances**: Correct debit/credit, account classification
4. **Dashboard Updates**: Real-time graph refresh without manual intervention
5. **Edge Cases**: Duplicates, reversals, boundary amounts

### Phase 3 Testing
1. **Complex Workflows**: Multi-step processes (payroll, disposal, etc.)
2. **Cross-Reference Integrity**: AFS notes, GL codes, account mapping
3. **Reconciliation**: Project totals vs main statements, inventory accuracy
4. **Dimensional Reporting**: Project P&L, asset class breakdowns

### Phase 4 Testing
1. **CFS Integration**: Cash flow categorization, source/use statements
2. **Movement Reconciliation**: Working capital changes, cash proceeds

---

## File Structure to Create/Modify

### New Modules (if needed)
```
registration/
  └── registration_handler.py
transact/
  └── navigation.py
cashbook/
  └── cashbook_handler.py
customers/
  ├── customer_handler.py
  └── masterfile.py
directors/
  ├── director_handler.py
  └── masterfile.py
employees/
  ├── payroll_handler.py
  └── masterfile.py
inventories/
  ├── inventory_handler.py
  └── masterfile.py
assets/
  └── asset_handler.py
projects/
  └── project_handler.py
adjustments/
  ├── adjustment_handler.py
  └── audit_trail.py
reporting/
  ├── dashboard.py
  ├── income_statement.py
  ├── balance_sheet.py
  ├── trial_balance.py
  ├── afs_notes.py
  └── cash_flow_statement.py (Phase 4)
auth/
  └── session.py
```

### Core Modifications
- `rigel_core.py`: Main application + shared `update_cce()` function
- All module handlers: Post transaction logic, dashboard refresh calls

---

## Validation Checklist

### Per Module (Template)
- [ ] All test cases reviewed
- [ ] Implementation logic confirmed
- [ ] Manual testing passed (Pass/Fail recorded)
- [ ] GL posting verified (debit/credit)
- [ ] TB balances after each transaction
- [ ] IS/BS/AFS impacts confirmed
- [ ] Dashboard updates without manual refresh
- [ ] No formula errors or blank fields
- [ ] All required fields present and validated
- [ ] Unique codes generated correctly
- [ ] Duplicate prevention working
- [ ] Edge cases tested

### Post-Phase Validation
- [ ] All tests in phase passed (100%)
- [ ] No data loss or corruption
- [ ] No breaking changes to prior phases
- [ ] Dashboard fully functional
- [ ] Report generation working
- [ ] Audit trail functional (if Phase 3+)

---

## Success Criteria

### Phase Completion
- **Phase 1**: All 18 + 4 = 22 tests PASS
- **Phase 2**: All 6 + 13 + 15 + 6 = 40 tests PASS
- **Phase 3**: All 8 + 10 + 5 + 6 = 29 tests PASS
- **Phase 4**: All 5 remaining tests PASS (after CFS built)

### Overall Success
- 109 tests PASS (100% of Phase 1–3)
- 5 tests DEFERRED (valid CFS dependency)
- Zero data loss
- Zero formula errors
- Dashboard fully functional
- All reconciliations correct

---

## Rollback Plan

In case of critical issues:

1. **Per Module**: If a module test fails, identify root cause
   - Check file path references
   - Verify GL account mappings
   - Confirm data store integrity
   - Fix and re-test until PASS

2. **Per Phase**: If phase cannot complete
   - Identify blocking issue
   - Apply fix
   - Re-run all tests in phase
   - Confirm no regressions in prior phases

3. **Full Project**: If critical data loss or corruption
   - Revert to last stable commit
   - Investigate root cause
   - Apply fix with comprehensive testing
   - Re-run all phases from Phase 1

---

## Documentation

- **Primary Reference**: `docs/requirements.md` (created)
- **Implementation Reference**: This file
- **Per-Module Notes**: To be added during implementation
- **Final Report**: To be generated post-completion

---

## Timeline Estimate

- **Phase 1**: 4-6 days (Foundation)
- **Phase 2**: 10-14 days (Core Transactions)
- **Phase 3**: 12-16 days (Advanced Features)
- **Phase 4**: 2-3 days (Deferred - CFS dependent)
- **Testing & Validation**: 2-3 days (integrated throughout)

**Total**: Approximately 30–42 days for complete implementation

---

## Next Steps

1. **Confirm approval** of this implementation plan
2. **Specify repository** for push (GitHub/GitLab/Bitbucket)
3. **Begin Phase 1** implementation (Registration + Transact)
4. **Proceed through phases** sequentially
5. **Document progress** with commit messages and status updates
6. **Push final version** to specified repository

---

*End of Implementation Plan*
