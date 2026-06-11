import pytest
from conftest import login, enable_flutter_semantics


# =========================
# TC-08: Borrow limit (REQ-04)
# MAX 3 books per member
# =========================
def test_borrow_book_limit(page, test_config):
    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())

    borrowed_books = sem_text.count("Đang mượn")

    borrow_buttons = page.locator(
        'flt-semantics[role="button"]:has-text("Mượn sách này")'
    ).count()

    # RULE 1: cannot exceed 3 books
    if borrowed_books > 3:
        pytest.fail(
            "BUG FOUND: Member is allowed to borrow more than 3 books (REQ-04 violation)."
        )

    # RULE 2: must block borrowing at limit
    if borrowed_books >= 3 and borrow_buttons > 0:
        pytest.fail(
            "BUG FOUND: Borrow limit reached (3 books) but system still allows borrowing."
        )


# =========================
# TC-09: View borrowed books (REQ-04)
# =========================
def test_view_borrowed_books(page, test_config):
    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())

    if "Đang mượn" not in sem_text:
        pytest.fail(
            "BUG FOUND: Borrowed books are not displayed for current user (REQ-04 violation)."
        )

    if not any(x in sem_text for x in ["Mã:", "BOOK"]):
        pytest.fail(
            "BUG FOUND: Borrowed book metadata is missing (REQ-04 violation)."
        )


# =========================
# TC-10: Return book (REQ-05)
# =========================
def test_return_book(page, test_config):
    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_before = " ".join(page.locator("flt-semantics").all_text_contents())

    return_buttons = page.locator(
        'flt-semantics:has-text("Trả sách")'
    )

    if return_buttons.count() == 0:
        pytest.fail(
            "BUG FOUND: No return button found although user has borrowed books (REQ-05 violation)."
        )

    return_buttons.first.click()

    page.wait_for_timeout(2000)

    sem_after = " ".join(page.locator("flt-semantics").all_text_contents())

    # RULE: book must be removed from borrowed state
    if sem_before == sem_after:
        pytest.fail(
            "BUG FOUND: Returning book does not update system state (REQ-05 violation)."
        )

    # optional stronger check
    if "Đang mượn" in sem_after and "Có sẵn" not in sem_after:
        pytest.fail(
            "BUG FOUND: Returned book does not change status to 'Có sẵn' (REQ-05 violation)."
        )


# =========================
# TC-19: Overdue handling (REQ-06)
# =========================
def test_return_overdue_book_warning(page, test_config):
    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())

    has_overdue = any(
        x in sem_text.lower()
        for x in ["quá hạn", "overdue"]
    )

    if not has_overdue:
        pytest.skip("SKIP: No overdue book available in current dataset (REQ-06).")

    return_buttons = page.locator(
        'flt-semantics:has-text("Trả sách")'
    )

    if return_buttons.count() == 0:
        pytest.fail(
            "BUG FOUND: Overdue book exists but cannot be returned (REQ-06 violation)."
        )

    return_buttons.first.click()

    page.wait_for_timeout(2000)

    sem_after = " ".join(page.locator("flt-semantics").all_text_contents())

    has_warning = any(
        x in sem_after.lower()
        for x in ["quá hạn", "overdue", "phạt", "penalty"]
    )

    if not has_warning:
        pytest.fail(
            "BUG FOUND: Overdue return does not trigger warning or penalty (REQ-06 violation)."
        )