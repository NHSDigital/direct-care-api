import functools

from assertpy import assert_that


def wrapper(assertion):
    @functools.wraps(assertion)
    def inner(*args, **kwargs):
        context = kwargs.get("context")
        expected = args[0]
        actual = args[1]
        try:
            assertion(*args, **kwargs)
        except Exception as e:
            print(e)
        finally:
            pass
            # allure.attach(expected, "Expected", allure.attachment_type.TEXT)
            # allure.attach(actual, "Actual", allure.attachment_type.TEXT)

    return inner


@wrapper
def wrap_assert_that(expected, actual, **kwargs):
    assert_that(actual).is_equal_to(expected)


wrapped_assert_that = wrapper(wrap_assert_that)
