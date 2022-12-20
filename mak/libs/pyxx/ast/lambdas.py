from motor_typing import TYPE_CHECKING


class LambdaExpression(object):

    def __init__(self, capture, attributes, declarator, compound_statement):
        # type: (Tuple[Optional[LambdaCapture], Optional[LambdaCaptureList]], List[Attribute], LambdaDeclarator, CompoundStatement) -> None
        self._capture = capture
        self._attributes = attributes
        self._declarator = declarator
        self._compound_statement = compound_statement

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_lambda_expression(self)


class TemplateLambdaExpression(LambdaExpression):

    def __init__(self, capture, template_parameter_list, attributes, requires_clause, declarator, compound_statement):
        # type: (Tuple[Optional[LambdaCapture], Optional[LambdaCaptureList]], List[TemplateParameter], List[Attribute], Optional[RequiresClause], LambdaDeclarator, CompoundStatement) -> None
        LambdaExpression.__init__(self, capture, attributes, declarator, compound_statement)
        self._template_parameter_list = template_parameter_list
        self._requires_clause = requires_clause

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_lambda_expression(self)


class LambdaCapture(object):
    pass


class LambdaCaptureDefaultCopy(LambdaCapture):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_lambda_capture_default_copy(self)


class LambdaCaptureDefaultReference(LambdaCapture):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_lambda_capture_default_reference(self)


class LambdaCaptureList(LambdaCapture):

    def __init__(self, capture_list):
        # type: (List[Capture]) -> None
        self._capture_list = capture_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_lambda_capture_list(self)


class Capture(object):
    pass


class SimpleCapture(Capture):

    def __init__(self, name, by_ref, pack, initializer):
        # type: (str, bool, bool, Optional[Expression]) -> None
        self._name = name
        self._by_ref = by_ref
        self._pack = pack
        self._initialzier = initializer

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_simple_capture(self)


class ThisCapture(Capture):

    def __init__(self, by_copy):
        # type: (bool) -> None
        self._by_copy = by_copy

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_this_capture(self)


class LambdaSpecifier(object):

    def __init__(self, specifier):
        # type: (str) -> None
        self._specifier = specifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_lambda_specifier(self)


class LambdaSpecifiers(object):
    MUTABLE = LambdaSpecifier('mutable')
    CONSTEXPR = LambdaSpecifier('constexpr')
    CONSTEVAL = LambdaSpecifier('consteval')
    STATIC = LambdaSpecifier('static')


class LambdaDeclarator(object):

    def __init__(
        self, parameter_list, lambda_specifier_seq, noexcept_specification, attribute_list, trailing_return_type,
        requires_clause
    ):
        # type: (Optional[ParameterClause], List[LambdaSpecifier], Optional[NoExceptSpecifier], List[Attribute], Optional[TypeId], Optional[object]) -> None
        self._parameter_list = parameter_list
        self._lambda_specifier_seq = lambda_specifier_seq
        self._noexcept_specification = noexcept_specification
        self._attribute_list = attribute_list
        self._trailing_return_type = trailing_return_type
        self._requires_clause = requires_clause

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_lambda_declarator(self)


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from . import Visitor
    from .expressions import Expression
    from .attributes import Attribute
    from .statements import CompoundStatement
    from .function import ParameterClause
    from .type import TypeId, NoExceptSpecifier
    from .constraints import RequiresClause
    from .template import TemplateParameter
