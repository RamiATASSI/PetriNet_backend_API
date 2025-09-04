"""
A small script transforming part of the code base documentation into a LaTeX file to include later
in a report
"""

import ast
import copy
from pathlib import Path
from dataclasses import dataclass


def latex_fmt(s: str) -> str:
    if not s:
        return None
    s_ = copy.deepcopy(s)
    s_ = s_.replace(r"_", r"\_") # Avoid subscripting
    s_ = s_.replace("\n\n", "\\\\") # Replace paragraph break
    s_ = s_.replace("\n", "") # Remove line break
    # TODO `code` -> \texttt{code}
    # TODO *smth* -> \textit{smth}
    return s_
@dataclass
class DocString:
    docstring: str
    args: list[tuple[str, str]] | None # Name, Desc
    raises: list[tuple[str, str]] | None # Exception, Desc
    return_: str | None # Desc
    type_: list[tuple[str, str]] | None # TypeVar, Desc
def strip_tags_from_doc(doc_: str) -> DocString:
    doc = copy.deepcopy(doc_)

    def index_all(s: str, f: str) -> list[int]:
        indexes = [-1]
        while True:
            indexes.append(s.find(f, indexes[-1]+1))
            if indexes[-1] == -1:
                return indexes[1:-1]

    def split_at_multiple_indexes(s: str, i: list[int]) -> list[str]:
        assert len(i) != 0

        i.insert(0, 0)
        i.append(len(s)+1)

        strs: list[str] = [s[i[i_]:i[i_+1]] for i_,_ in enumerate(i[:-1])]
        return strs

    # Detecting
    args_indexes = index_all(doc, ":param ")
    raises_indexes = index_all(doc, ":raises ")
    return_index = index_all(doc, ":return:")
    type_indexes = index_all(doc, ":type ")

    flat_indexes = copy.deepcopy(args_indexes)
    flat_indexes.extend(raises_indexes)
    flat_indexes.extend(return_index)
    flat_indexes.extend(type_indexes)

    assert len(return_index) <= 1
    if len(flat_indexes) == 0:
        return DocString(doc_, None, None, None, None)

    # Splitting
    splited = split_at_multiple_indexes(doc, flat_indexes)
    cum_index = 0
    doc_string = splited[0]

    cum_index += 1
    args = []
    raises = []
    return_ = ""
    type_ = []
    for _ in args_indexes:
        args.append(splited[cum_index])
        cum_index += 1
    for _ in raises_indexes:
        raises.append(splited[cum_index])
        cum_index += 1
    for _ in return_index:
        return_ = splited[cum_index]
        cum_index += 1
    for _ in type_indexes:
        type_.append(splited[cum_index])
        cum_index += 1

    # Formatting
    def arg_process(s: str):
        sep_i = s.find(':', 1)
        arg_name = s[len(":param "): sep_i]
        desc = s[sep_i+1:-1]
        return arg_name, desc
    def raise_process(s: str):
        sep_i = s.find(':', 1)
        ex_name = s[sep_i+1:-1]
        desc = s[sep_i+1:-1]
        return ex_name, desc
    def return_process(s: str):
        sep_i = s.find(':', 1)
        desc = s[sep_i+1:-1]
        return desc
    def type_process(s: str):
        sep_i = s.find(':', 1)
        type_name = s[sep_i+1:-1]
        desc = s[sep_i+1:-1]
        return type_name, desc

    return DocString(
        docstring=doc_string,
        args= [arg_process(arg) for arg in args] if args else None,
        raises=[raise_process(raise_) for raise_ in raises] if raises else None,
        return_= return_process(return_) if return_ else None,
        type_ = [type_process(type_) for type_ in type_] if type_ else None,
    )

@dataclass
class MemberDoc: # Variable
    name: str
    doc: str

    def to_latex(self) -> str:
        return f"\\item \\textbf{latex_fmt(self.name)}\n{self.doc}"

@dataclass
class FunctionDoc:
    name: str
    class_: str | None
    doc: str
    args: list[tuple[str, str | None, str]] # (Name, Type?, Desc)
    raises: list[tuple[str, str]] # (Type, Desc)
    return_: tuple[str | None, str] | None # (Type, Desc)

    def format_arg(self, arg: tuple[str, str|None, str]) -> str:
        if not arg[1]:
            return "\\textit{" + latex_fmt(arg[0]) + "}" + latex_fmt(arg[2])
        return "\\textit{" + latex_fmt(arg[0]) + "}" + " \\texttt{" + (arg[1]) + "}" + latex_fmt(arg[2])

    def format_raise(self, arg: tuple[str, str]) -> str:
        return "\\texttt{" + latex_fmt(arg[0]) + "}" + latex_fmt(arg[1])

    def format_return(self, arg: tuple[str, str]) -> str:
        if not arg[0]:
            return latex_fmt(arg[1])
        return "\\texttt{" + latex_fmt(arg[0]) + "}" + latex_fmt(arg[1])

    def to_latex(self) -> str:
        title = f"{self.class_}.\\textbf{{{self.name}}}" if self.class_ else f"\\textbf{{{self.name}}}"
        if not self.args and not self.raises and not self.return_:
            return title + '\n' + self.doc + '\n'

        args = "\n\\item " + "\n\\item ".join([self.format_arg(arg) for arg in self.args]) if self.args else ''
        raise_ = "\n\\item " + "\n\\item ".join([self.format_raise(r) for r in self.raises]) if self.raises else ''
        return_ = f"\n\\item {self.format_return(self.return_)}" if self.return_ else ''
        return (latex_fmt(title) + '\n' + latex_fmt(self.doc) + '\n' + "\\begin{itemize}" +
                args + raise_ + return_
                + '\n' + "\\end{itemize}" + '\n')

@dataclass
class ClassDoc:
    name: str
    doc: str
    superclass: list[str] | None
    #members: list[MemberDoc] | None
    functions: list[FunctionDoc] | None
    outer_class: str | None
    #inner_classes: list['ClassDoc'] | None
    types: list[tuple[str, str]]

    def format_type(self, t: tuple[str, str]) -> str:
        return f"\\texttt{{{t[0]}}} \\texttt{{{t[1]}}}"

    def to_latex(self) -> str:
        title = "\\textit{" + (f"{self.outer_class}.{self.name}" if self.outer_class else self.name) + "}"
        implements = "(" + ", ".join(self.superclass) + ")" if self.superclass else ""
        functions = "\\begin{itemize}" + "\n\\item " + "\n\\item ".join([f.to_latex() for f in self.functions]) + "\\end{itemize}" if self.functions else ""
        #inner_classes =
        types = "\n\\item " + "\n\\item ".join([self.format_type(t) for t in self.types]) if self.types else ""

        return title + implements + '\n' + self.doc + '\n' + functions


@dataclass
class ModuleDoc:
    name: str
    doc: str
    members: list[MemberDoc] | None
    functions: list[FunctionDoc] # Static functions
    classes: list[ClassDoc]

    def to_latex(self) -> str:
        header = f"\\subsection{{{latex_fmt(self.name)}}}\n"
        desc = latex_fmt(self.doc) + "\n\n"
        members_doc = "\n\n".join([m.to_latex() for m in self.members]) if self.members else ""
        functions_doc = "\n\n".join([f.to_latex() for f in self.functions]) if self.functions else ""
        classes_doc = "\n\n".join([c.to_latex() for c in self.classes]) if self.classes else ""
        return header + desc + members_doc + functions_doc + classes_doc

@dataclass
class ADT: # Abstract Documentation Tree
    modules: list[ModuleDoc]

    def to_latex(self) -> str:
        i = ""
        for m in self.modules:
            i += m.to_latex()
        return i

def parse_file(src_dir: str, filepath_: str) -> ast.Module | None:
    filepath = Path(src_dir + filepath_ + ".py")
    if not filepath.exists() or not filepath.is_file():
        print(f'File {filepath} does not exist or is not a file.')
        raise FileNotFoundError(filepath)
    with filepath.open("r", encoding="utf-8") as file:
        source = file.read()

    return ast.parse(source, filename=filepath_)

def convert_file_to_doc(a: ast.Module, name: str) -> ModuleDoc:
    def convert_function_to_function_doc(f: ast.FunctionDef, parent: str | None) -> FunctionDoc:
        def annotation_to_str(annotation):
            return ast.unparse(annotation)

        docstring = strip_tags_from_doc(ast.get_docstring(f))
        # Args processing
        if docstring.args:

            types = {}
            for arg in f.args.args + f.args.kwonlyargs:
                types[arg.arg] = annotation_to_str(arg.annotation)
            if f.args.vararg:
                types[f"*{f.args.vararg.arg}"] = annotation_to_str(f.args.vararg.annotation)
            if f.args.kwarg:
                types[f"**{f.args.kwarg.arg}"] = annotation_to_str(f.args.kwarg.annotation)
            assert len(docstring.args) == len(types)

            args = []
            for i in range(len(types)):
                arg = docstring.args[i]
                args.append((arg[0], types[arg[0]], arg[1]))
        else:
            args = None

        return_type = annotation_to_str(f.returns) if f.returns else None

        return FunctionDoc(
            name=f.name,
            class_= parent.name if isinstance(parent, ast.ClassDef) else parent,
            doc=docstring.docstring,
            args=args,
            raises=docstring.raises,
            return_=(return_type, docstring.return_)
        )

    def convert_class_to_class_doc(c: ast.ClassDef, outer_class: str|None) -> ClassDoc:

        #members = []
        functions = [node for node in c.body if isinstance(node, ast.FunctionDef)]
        #inner_classes = [node for node in c.body if isinstance(node, ast.ClassDef)]

        docstring = strip_tags_from_doc(ast.get_docstring(c))

        return ClassDoc(
            name=c.name,
            doc=docstring.docstring,
            superclass=[ast.unparse(base) for base in c.bases],
            #members=,
            functions=[convert_function_to_function_doc(function, c.name) for function in functions],
            outer_class=outer_class,
            #inner_classes=[convert_class_to_class_doc(c, c.name) for c in inner_classes],
            types=docstring.type_
        )

    def convert_variable_to_member_doc(v: ast.Name) -> MemberDoc:
        pass

    members = [] # [node for node in a.body if isinstance(node, ast.Name)]
    static_functions = [node for node in a.body if isinstance(node, ast.FunctionDef)]
    top_level_class = [node for node in a.body if isinstance(node, ast.ClassDef)]

    return ModuleDoc(
        name=name,
        doc=ast.get_docstring(a),
        members=[convert_variable_to_member_doc(member) for member in members]
            if members else None,
        functions=[convert_function_to_function_doc(static_functions[0], None)]
            if static_functions else None,
        classes=[convert_class_to_class_doc(c, None) for c in top_level_class]
            if top_level_class else None
    )

SRC_PATH = "src/PetriNet_algo/"

def main():
    files_to_parse = [
        "data_structure/dict_list_builder",
        #"object/place",
        #"object/token", "object/transition",
        #"object/transition/condition", "object/transition/operator"
    ]
    output_filepath = "doc2latex2.tex"

    # Generate
    parsed_files = [(parse_file(SRC_PATH, file_to_parse), file_to_parse) for file_to_parse in files_to_parse]
    assert not parsed_files.__contains__(None)
    # Convert
    adt = ADT([convert_file_to_doc(f, n) for (f, n) in parsed_files])
    # Write
    with open(output_filepath, "w") as latex_file:
        latex_file.write(adt.to_latex())

if __name__ == "__main__":
    main()
