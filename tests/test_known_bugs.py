import pytest
from conftest import (
    login,
    enable_flutter_semantics,
    flutter_fill,
    flutter_click_button,
)


def test_bug_borrow_limit(page, test_config):
    """
    BUG-01
    Thành viên có thể mượn quá số sách quy định.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    has_borrowed_book = "Đang mượn" in sem_text

    borrow_buttons = page.locator(
        'flt-semantics[role="button"]:has-text("Mượn sách này")'
    )

    if has_borrowed_book and borrow_buttons.count() > 0:
        pytest.fail(
            "BUG FOUND: User already has borrowed books "
            "but system still allows borrowing more."
        )


def test_bug_overdue_return_no_warning(page, test_config):
    """
    BUG-02
    Trả sách quá hạn nhưng không có cảnh báo.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    page.wait_for_timeout(2000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    # Nếu dữ liệu test không có sách quá hạn thì bỏ qua
    if "Quá hạn" not in sem_text and "Overdue" not in sem_text:
        pytest.skip(
            "No overdue book found in current dataset"
        )

    return_buttons = page.locator(
        'flt-semantics:has-text("Trả sách")'
    )

    if return_buttons.count() == 0:
        pytest.fail(
            "BUG FOUND: Overdue book exists but no return button."
        )

    return_buttons.first.click()

    page.wait_for_timeout(2000)

    sem_text_after = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    assert (
        "quá hạn" in sem_text_after.lower()
        or "overdue" in sem_text_after.lower()
        or "phạt" in sem_text_after.lower()
    ), (
        "BUG FOUND: Overdue book returned without warning."
    )


def test_bug_login_email_spaces(page, test_config):
    """
    BUG-03
    Email có khoảng trắng bất thường.
    """

    page.goto(
        test_config["base_url"],
        wait_until="networkidle",
        timeout=60000
    )

    enable_flutter_semantics(page)

    flutter_fill(
        page,
        "Email",
        f"   {test_config['email']}   "
    )

    flutter_fill(
        page,
        "Mật khẩu",
        test_config["password"]
    )

    flutter_click_button(page, "Đăng nhập")

    page.wait_for_timeout(3000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    if test_config["display_name"] in sem_text:
        pytest.fail(
            "BUG FOUND: Login accepted email with leading/trailing spaces."
        )


def test_bug_multiple_click_borrow(page, test_config):
    """
    BUG-04
    Double click tạo nhiều lượt mượn.
    """

    login(page, test_config)
    enable_flutter_semantics(page)

    borrow_buttons = page.locator(
        'flt-semantics[role="button"]:has-text("Mượn sách này")'
    )

    if borrow_buttons.count() == 0:
        pytest.skip("No borrowable book found")

    borrow_buttons.first.click()
    borrow_buttons.first.click()

    page.wait_for_timeout(2000)

    sem_text = " ".join(
        page.locator("flt-semantics").all_text_contents()
    )

    if sem_text.count("Đang mượn") > 1:
        pytest.fail(
            "BUG FOUND: Double click may create duplicate borrow records."
        )