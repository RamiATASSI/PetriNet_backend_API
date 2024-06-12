import io
import sys
import unittest

from PetriNet_algo.deserializer import ColorDeserializer

if __name__ == '__main__':
    unittest.main()


class TestClassDeserializerGetInstance(unittest.TestCase):
    def setUp(self):
        self.deserializer = ColorDeserializer()

    def test_class_with_valid_constructor_returns_instance(self):
        class_code = """
        class MyClass:
            def __init__(self):
                self.attribute = "Hello, world!"
        """
        instance = self.deserializer.get_instance(class_code)
        self.assertEqual(instance.attribute, "Hello, world!")

    def test_class_with_invalid_syntax_raises_syntax_error(self):
        class_code = """
        class MyClass
            def __init__(self):
                self.attribute = "Hello, world!"
        """
        with self.assertRaises(SyntaxError):
            self.deserializer.get_instance(class_code)

    def test_class_with_non_callable_constructor_raises_type_error(self):
        class_code = """
        class MyClass:
            __init__ = "Hello, world!"
        """
        with self.assertRaises(TypeError):
            self.deserializer.get_instance(class_code)

    def test_class_code_cannot_access_outer_classes(self):
        class OuterClass:
            pass

        class_code = """
        class MyClass:
            def __init__(self):
                self.instance = OuterClass()
        """
        with self.assertRaises(NameError):
            self.deserializer.get_instance(class_code)

    def test_outer_class_cannot_access_class_code(self):
        class_code = """
        class MyClass:
            pass
        """
        instance = self.deserializer.get_instance(class_code)

        with self.assertRaises(NameError):
            wrong_instance = MyClass()


class TestClassDeserializerGenerateClassCode(unittest.TestCase):
    def setUp(self):
        self.deserializer = ColorDeserializer()
        self.data = {
            "class_name": "Humans",
            "attributes": [
                {"attribute_name": "attribute11", "attribute_value": "1"},
                {"attribute_name": "attribute12", "attribute_value": "'value1'"}],
            "functions": [
                {"function_name": "function11", "function_core": "return self.attribute11"},
                {"function_name": "function12", "function_core": "self.attribute11 = 3; print(self.attribute11)"}]
        }

    def test_class_code_generation(self):
        expected_output = """class Humans:
    def __init__(self):
        self.attribute11 = 1
        self.attribute12 = 'value1'
    def function11(self):
        return self.attribute11
    def function12(self):
        self.attribute11 = 3; print(self.attribute11)
"""
        result = self.deserializer.generate_class_code(self.data)
        self.assertEqual(result, expected_output)

    def test_class_code_gen_and_get_instance(self):
        instance = self.deserializer.compile(self.data)
        self.assertEqual(instance.function11(), 1)
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        instance.function12()
        print_output = buffer.getvalue()
        sys.stdout = old_stdout

        # Check the output
        self.assertEqual(print_output.strip(), '3', "The function output is not 3")
