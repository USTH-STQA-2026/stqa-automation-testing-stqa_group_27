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
from conftest import (
    login,
    enable_flutter_semantics,
    flutter_click_button,
)


def test_borrow_book_limit(page, test_config):
    """
    TC-08: Thành viên không được mượn quá số sách quy định.

    Bug cần phát hiện:
    User đã có sách đang mượn nhưng hệ thống vẫn tiếp tục
    hiển thị và cho phép mượn thêm.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    # Tài khoản hiện tại đã có sách đang mượn
    has_borrowed_book = "Đang mượn" in sem_text

    borrow_buttons = page.locator(
        'flt-semantics[role="button"]:has-text("Mượn sách này")'
    )

    borrow_button_count = borrow_buttons.count()

    print("Borrow button count:", borrow_button_count)

    # Nếu đã có sách đang mượn mà vẫn còn rất nhiều nút mượn
    # thì đây là dấu hiệu bug business rule
    if has_borrowed_book and borrow_button_count > 0:
        pytest.fail(
            "BUG FOUND: User already has borrowed books "
            "but system still allows borrowing more books."
        )


def test_view_borrowed_books(page, test_config):
    """
    TC-09: Xem danh sách sách đang mượn.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    assert "Đang mượn" in sem_text, (
        "Borrowed books are not displayed"
    )

    assert "BOOK" in sem_text, (
        "Book information is not displayed"
    )


def test_return_book(page, test_config):
    """
    TC-10: Trả sách.

    Tạm thời skip nếu Flutter semantics
    chưa expose nút 'Trả sách'.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    if "Trả sách" not in sem_text:
        pytest.skip(
            "Return button not found in semantics tree"
        )

    return_buttons = page.locator(
        'flt-semantics:has-text("Trả sách")'
    )

    if return_buttons.count() == 0:
        pytest.skip(
            "No borrowed book available for return"
        )

    count_before = return_buttons.count()

    return_buttons.first.click()

    page.wait_for_timeout(2000)

    count_after = page.locator(
        'flt-semantics:has-text("Trả sách")'
    ).count()

    assert count_after < count_before, (
        "Return book failed"
    )

def test_return_overdue_book_warning(page, test_config):
    """
    TC-19: Return overdue book

    Bug expected:
    User returns an overdue book but system does not show
    any overdue warning or penalty notification.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text_before = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    print(sem_text_before)

    # Chỉ chạy khi dữ liệu test thực sự có sách quá hạn
    if "Quá hạn" not in sem_text_before and "Overdue" not in sem_text_before:
        pytest.skip(
            "No overdue book found in current test data"
        )

    # Tìm nút trả sách
    return_buttons = page.locator(
        'flt-semantics:has-text("Trả sách")'
    )

    if return_buttons.count() == 0:
        pytest.skip(
            "No return button available"
        )

    return_buttons.first.click()

    page.wait_for_timeout(2000)

    sem_text_after = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    print(sem_text_after)

    assert (
        "quá hạn" in sem_text_after.lower()
        or "overdue" in sem_text_after.lower()
        or "phạt" in sem_text_after.lower()
        or "penalty" in sem_text_after.lower()
    ), (
        "BUG FOUND: Overdue book returned without "
        "warning, penalty, or overdue notification."
    )