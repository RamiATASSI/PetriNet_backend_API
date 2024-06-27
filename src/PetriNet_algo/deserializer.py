import re
import textwrap


class ColorDeserializer:
    def __init__(self):
        self.classes = {}

    def compile(self, color_data):
        class_code = self.generate_class_code(color_data)
        instance = self.get_instance(class_code)
        return instance

    def get_instance(self, class_code: str):
        try:
            # Remove leading whitespace from the class code
            class_code = textwrap.dedent(class_code)

            # Execute the class code in the context of self.classes
            exec(class_code, self.classes)

            # Use regex to get the class name
            class_name = re.search(r'class\s+(\w+)', class_code).group(1)

            # Instantiate the class
            instance = self.classes[class_name]()

            return instance
        except SyntaxError:
            raise SyntaxError("Error: The provided class code is not valid Python code.")
        except AttributeError:
            raise AttributeError("Error: The class does not have a callable constructor.")
        except TypeError:
            raise TypeError("Error: The class's constructor is not callable.")
        except NameError:
            raise NameError("Error: The class is trying to access a name that is not defined.")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

    def generate_class_code(self, color_data):
        class_name = color_data['class_name']
        attributes = color_data['attributes']
        functions = color_data['functions']

        class_code = f"class {class_name}:\n"
        class_code += "    def __init__(self):\n"

        for attribute in attributes:
            attribute_name = attribute['attribute_name']
            attribute_value = attribute['attribute_value']
            class_code += f"        self.{attribute_name} = {attribute_value}\n"

        for function in functions:
            function_name = function['function_name']
            function_core = function['function_core']
            arguments = function.get('arguments', '')
            if arguments:
                arguments = 'self, ' + arguments
            else:
                arguments = 'self'
            class_code += f"    def {function_name}({arguments}):\n"
            class_code += f"        {function_core}\n"

        return class_code



def main() -> None:
    # Usage example
    class_code1 = """
    class MyClass1:
        def __init__(self):
            self.attribute = "Hello, world!"

        def print_attribute(self):
            print(self.attribute)
    """
    # Create a ClassDeserializer
    deserializer = ColorDeserializer()

    # Get an instance of the first class
    instance1 = deserializer.get_instance(class_code1)

    # Print the value of the attribute for the instance
    instance1.print_attribute()  # Outputs: Hello, world!


if __name__ == '__main__':
    main()
