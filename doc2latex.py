"""
A small script transforming part of the code base documentation into a LaTeX file to include later
in a report
"""

import ast
import os

SRC_PATH = "src/PetriNet_algo/"
FILES_TO_CONVERT = [SRC_PATH + file + ".py" for file in
    [
        "data_structure/dict_list_builder",

        #"object/place",
        "object/token", "object/transition",
        "object/transition/condition", "object/transition/operator"
    ]
]

def wrap_in_texttt(s) -> str:
    return r"\texttt{%s}" % s

def extract_docstrings(filepath) -> list:
    with open(filepath, "r") as file:
        source = file.read()

    tree = ast.parse(source, filename=filepath)
    filename = filepath.split("/")[-1]

    doc_entries = []

    # 1. Module-level docstring
    module_doc = ast.get_docstring(tree)

    if module_doc:
        # The [:-3] removes the ".py" of the filename
        doc_entries.append(("Module", wrap_in_texttt(filename[:-3]), module_doc.replace('\n', ' ')))

    # 2. Walk through AST to find classes, functions, and variable-like docstrings
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            doc_entries.append(("Function", wrap_in_texttt(node.name), doc.replace('\n', ' ')))

        elif isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node)
            if class_doc:
                doc_entries.append(("Class", wrap_in_texttt(node.name), class_doc.replace('\n', ' ')))
            else:
                doc_entries.append(("Class", wrap_in_texttt(node.name), "MISSING DOCUMENTATION FOR THIS CLASS"))

            # Also extract method docstrings inside the class
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = ast.get_docstring(item)
                    if method_doc:
                        full_name = f"{node.name}.{item.name}"
                        doc_entries.append(("Method", wrap_in_texttt(full_name), method_doc.replace('\n', ' ')))
                    else:
                        doc_entries.append(("Class", wrap_in_texttt(node.name), "MISSING DOCUMENTATION FOR THIS CLASS"))

    return doc_entries

def format_docstring_for_latex(docstring: str) -> str:
    import re
    def reformat_param_docs(docstring: str):
        if not docstring:
            return docstring

        # ":param var_name: description"
        optional_tick = r"(\')?"
        not_next_tag = r""
        # r'(:param\s+\S+:\s*)(.*?)(?=\n(:param|:type|:raise|:return|$))'

        param_pattern  = re.compile(r':param\s+(\w+)\s*:\s*([^:]+)')
        type_pattern   = re.compile(r':type\s+\'(\w+)\'\s*:\s*([^:]+)')
        raise_pattern  = re.compile(r':raise\s+(\w+)\s*:\s*([^:]+)')
        return_pattern = re.compile(r':return\s*:\s*([^:]+)')

        param_lines  = param_pattern.findall(docstring)
        type_lines   = type_pattern.findall(docstring)
        raise_lines  = raise_pattern.findall(docstring)
        return_lines = return_pattern.findall(docstring)

        # Replace each param line with LaTeX item
        if param_lines:
            print("Params:", param_lines)
            param_items = [
                f"  \\item[P] \\texttt{{{name}}}: {desc}"
                for name, desc in param_lines
            ]
        else:
            param_items = []
        if type_lines:
            print("Types:", type_lines)
            type_items = [
                f"  \\item[T] \\texttt{{{name}}}: {desc}"
                for name, desc in type_lines
            ]
        else:
            type_items = []
        if raise_lines:
            print("Raises:", raise_lines)
            raise_items = [
                f"  \\item[R] \\texttt{{{name}}}: {desc}"
                for name, desc in raise_lines
            ]
        else:
            raise_items = []
        if return_lines:
            print("Returns:", return_lines)
            return_items = [
                f"  \\item[Ret]: {desc}"
                for desc in return_lines
            ]
        else: return_items = []

        latex_items = param_items
        latex_items.extend(type_items)
        latex_items.extend(raise_items)
        latex_items.extend(return_items)

        # There are no items
        if not latex_items:
            return docstring

        for i, it in enumerate(latex_items):
            if it.endswith('\\\\'):
                latex_items[i] = it[:-2]

        # Join and wrap with itemize
        latex_block = "\\begin{itemize}\n" + "\n".join(latex_items) + "\n\\end{itemize}"

        # Remove original param lines from docstring
        cleaned_docstring = re.sub(param_pattern, '', docstring)
        cleaned_docstring = re.sub(type_pattern, '', cleaned_docstring)
        cleaned_docstring = re.sub(raise_pattern, '', cleaned_docstring)
        cleaned_docstring = re.sub(return_pattern, '', cleaned_docstring)

        # Combine cleaned docstring and new LaTeX block
        final_docstring = cleaned_docstring.strip() + "\n\n" + latex_block
        return final_docstring

    def reformat_backtick2texttt(doc: str) -> str:
        return doc

    def reformat_list2itemize(doc: str) -> str:
        return doc

    if docstring is None:
        return "No documentation available."

    docstring = docstring.replace("_", r"\_")
    docstring = docstring.replace("\n", "\\\\\n")

    docstring = reformat_param_docs(docstring)
    docstring = reformat_backtick2texttt(docstring)
    docstring = reformat_list2itemize(docstring)

    return docstring


def extract_and_generate_latex(filepaths, output_filepath):
    with open(output_filepath, "w") as latex_file:
        latex_file.write("% Automatically generated by doc2latex.py\n")

        # For all filepath
        for filepath in filepaths:
            if os.path.exists(filepath):
                modulename = filepath.replace(SRC_PATH, "")
                latex_file.write(f"\n\n\\subsubsection{{\\texttt{{{format_docstring_for_latex(modulename)}}} }}\n")
                latex_file.write("\\begin{itemize}\n")
                docstrings = extract_docstrings(filepath)
                for doc_type, name, doc in docstrings:
                    latex_file.write(f"\\item \\textbf{{{doc_type}:}} {format_docstring_for_latex(name)} \\\\\n")
                    latex_file.write(f"{format_docstring_for_latex(doc)}" + "\n\n")
                latex_file.write("\\end{itemize}\n")


def example():
    output_latex_file = "documentation_report.tex"
    extract_and_generate_latex(FILES_TO_CONVERT, output_latex_file)

if __name__ == "__main__":
    example()
