class ClassI(object):
    from ..module_1 import Class1


def function():
    from ...module_a import ClassA

    def inner_function():
        from ...subpackage_a.module_1 import Class1

        class InnerClass(object):
            from external import module_a

    return inner_function
