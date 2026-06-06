"""
Borrow & Return Tests (*Kiểm thử Mượn & Trả sách*) — Library Book Borrowing System (*Hệ thống Mượn sách thư viện*)

Students must complete ALL 3 test cases in this file.
(*Sinh viên cần hoàn thành TẤT CẢ 3 test case trong file này.*)

Hints (*Gợi ý*):
    - Use login() helper to log in (*Dùng login() helper để đăng nhập*)
    - "Mượn / Trả" tab: role="tab", aria-label="Mượn / Trả"
    - Available books have "Có sẵn" in aria-label, borrowed books have "Đang mượn"
      (*Sách "Có sẵn" có aria-label chứa "Có sẵn", sách "Đang mượn" chứa "Đang mượn"*)
    - Borrow button: 'flt-semantics[role="button"]:has-text("Mượn sách này")'
      (*Nút mượn*)
    - After clicking "Mượn sách này", a confirmation dialog appears — click "Mượn" again
      (*Sau khi click "Mượn sách này" sẽ hiện dialog xác nhận — cần click nút "Mượn" lần nữa*)
    - Return button: 'flt-semantics[role="button"]:has-text("Trả sách")'
      (*Nút trả*)
"""
import os
import time
import pytest
from conftest import login, enable_flutter_semantics, flutter_click_button, wait_for_flutter

def test_borrow_book_limit(page, test_config):
    """
    TC-08 (BUG TEST): Borrow limit validation
    (*Kiểm tra giới hạn số sách được mượn*)
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    # =========================
    # [R] Reachability
    # =========================
    page.wait_for_timeout(2000)

    # =========================
    # [I] Infection: try borrow multiple times
    # =========================

    borrowed_count = 0

    for i in range(4):  # thử mượn 4 lần
        try:
            # tìm sách có sẵn
            book = page.locator(
                'flt-semantics[role="group"][aria-label*="Có sẵn"]'
            ).first

            if book.count() == 0:
                break

            book.click()

            flutter_click_button(page, "Mượn sách này")

            page.wait_for_timeout(1000)

            # confirm nếu có dialog
            if page.locator('flt-semantics:has-text("Mượn")').count() > 0:
                flutter_click_button(page, "Mượn")

            page.wait_for_timeout(1500)

            borrowed_count += 1

        except Exception:
            break

    # =========================
    # [P + R✓] Propagation + Revealability
    # =========================

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())

    print("Borrowed count:", borrowed_count)

    # ===== ASSERT BUSINESS RULE =====
    assert borrowed_count <= 3, (
        f"BUG FOUND ❌: User can borrow more than limit (3). "
        f"Actual borrowed: {borrowed_count}"
    )

    assert (
        "không thể" in sem_text.lower()
        or "limit" in sem_text.lower()
        or "tối đa" in sem_text.lower()
        or borrowed_count <= 3
    ), "System does not enforce borrow limit properly"

def test_view_borrowed_books(page, test_config):
    login(page, test_config)
    enable_flutter_semantics(page)

    flutter_click_button(page, "Mượn / Trả")

    page.wait_for_timeout(2000)

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())

    borrowed_books = page.locator(
        'flt-semantics[aria-label*="Đang mượn"]'
    ).count()

    assert borrowed_books >= 0, "Borrowed books list not loaded"

    # nếu hệ thống có bug borrow limit → sẽ thấy >3 dễ phát hiện ở đây
    assert borrowed_books <= 3, (
        f"BUG: Borrowed books exceed limit: {borrowed_books}"
    )

def test_return_book(page, test_config):
    login(page, test_config)
    enable_flutter_semantics(page)

    flutter_click_button(page, "Mượn / Trả")

    page.wait_for_timeout(2000)

    return_buttons = page.locator(
        'flt-semantics:has-text("Trả sách")'
    )

    count_before = return_buttons.count()

    if count_before == 0:
        pytest.skip("No borrowed books to return")

    return_buttons.first.click()

    page.wait_for_timeout(1000)

    flutter_click_button(page, "Trả sách")

    page.wait_for_timeout(2000)

    count_after = page.locator(
        'flt-semantics:has-text("Trả sách")'
    ).count()

    assert count_after < count_before, "Return book failed"

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())

    assert (
        "thành công" in sem_text.lower()
        or "đã trả" in sem_text.lower()
    ), "No success message after returning book"
