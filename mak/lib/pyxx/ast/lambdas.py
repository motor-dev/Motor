from typing import List, Optional, Tuple
from . import Visitor
from .base import Expression, Attribute
from .statements import CompoundStatement
from .function import ParameterClause
from .type import TypeId, NoExceptSpecifier
from .constraints import RequiresClause
from .template import TemplateParameter, TemplateParameterList, AmbiguousTemplateParameterList, \
    AbstractTemplateParameterList


class Capture(object):
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class LambdaCapture(object):
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class LambdaCaptureList(LambdaCapture):

    def __init__(self, capture_list: List[Capture]):
        self.capture_list = capture_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_lambda_capture_list(self)

    def accept_capture_list(self, visitor: Visitor) -> None:
        for capture in self.capture_list:
            capture.accept(visitor)


class LambdaSpecifier(object):

    def __init__(self, specifier: str):
        self.specifier = specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_lambda_specifier(self)


class LambdaSpecifiers(object):
    MUTABLE = LambdaSpecifier('mutable')
    CONSTEXPR = LambdaSpecifier('constexpr')
    CONSTEVAL = LambdaSpecifier('consteval')
    STATIC = LambdaSpecifier('static')


class LambdaDeclarator(object):

    def __init__(
            self, parameter_list: Optional[ParameterClause], lambda_specifier_seq: List[LambdaSpecifier],
            noexcept_specification: Optional[NoExceptSpecifier],
            attribute_list: List[Attribute], trailing_return_type: Optional[TypeId],
            requires_clause: Optional[RequiresClause]
    ):
        self.parameter_list = parameter_list
        self.lambda_specifier_seq = lambda_specifier_seq
        self.noexcept_specification = noexcept_specification
        self.attribute_list = attribute_list
        self.trailing_return_type = trailing_return_type
        self.requires_clause = requires_clause

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_lambda_declarator(self)

    def accept_parameter_list(self, visitor: Visitor) -> None:
        if self.parameter_list is not None:
            self.parameter_list.accept(visitor)

    def accept_noexceot_specification(self, visitor: Visitor) -> None:
        if self.noexcept_specification:
            self.noexcept_specification.accept(visitor)

    def accept_lambda_specifier_seq(self, visitor: Visitor) -> None:
        for lambda_specifier in self.lambda_specifier_seq:
            lambda_specifier.accept(visitor)

    def accept_attribute_list(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_trailing_return_type(self, visitor: Visitor) -> None:
        if self.trailing_return_type is not None:
            self.trailing_return_type.accept(visitor)

    def accept_requires_clause(self, visitor: Visitor) -> None:
        if self.requires_clause is not None:
            self.requires_clause.accept(visitor)


class LambdaExpression(object):

    def __init__(self, capture: Tuple[Optional[LambdaCapture], Optional[LambdaCaptureList]],
                 attributes: List[Attribute], declarator: LambdaDeclarator, compound_statement: CompoundStatement):
        self.capture = capture
        self.attributes = attributes
        self.declarator = declarator
        self.compound_statement = compound_statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_lambda_expression(self)

    def accept_capture(self, visitor: Visitor) -> None:
        if self.capture[0] is not None:
            self.capture[0].accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_declarator(self, visitor: Visitor) -> None:
        self.declarator.accept(visitor)

    def accept_compound_statement(self, visitor: Visitor) -> None:
        self.compound_statement.accept(visitor)


class TemplateLambdaExpression(LambdaExpression):

    def __init__(self, capture: Tuple[Optional[LambdaCapture], Optional[LambdaCaptureList]],
                 template_parameter_list: List[List[TemplateParameter]],
                 attributes: List[Attribute], requires_clause: Optional[RequiresClause], declarator: LambdaDeclarator,
                 compound_statement: CompoundStatement):
        LambdaExpression.__init__(self, capture, attributes, declarator, compound_statement)
        if len(template_parameter_list) == 1:
            self.template_parameter_list = TemplateParameterList(
                template_parameter_list[0])  # type: AbstractTemplateParameterList
        else:
            self.template_parameter_list = AmbiguousTemplateParameterList(template_parameter_list)
        self.requires_clause = requires_clause

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_lambda_expression(self)

    def accept_template_parameter_list(self, visitor: Visitor) -> None:
        self.template_parameter_list.accept(visitor)

    def accept_constraint(self, visitor: Visitor) -> None:
        if self.requires_clause is not None:
            self.requires_clause.accept(visitor)


class LambdaCaptureDefaultCopy(LambdaCapture):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_lambda_capture_default_copy(self)


class LambdaCaptureDefaultReference(LambdaCapture):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_lambda_capture_default_reference(self)


class SimpleCapture(Capture):

    def __init__(self, name: str, by_ref: bool, pack: bool, initializer: Optional[Expression]):
        self.name = name
        self.by_ref = by_ref
        self.pack = pack
        self.initializer = initializer

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_simple_capture(self)

    def accept_initializer(self, visitor: Visitor) -> None:
        if self.initializer is not None:
            self.initializer.accept(visitor)


class ThisCapture(Capture):

    def __init__(self, by_copy: bool):
        self.by_copy = by_copy

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_this_capture(self)
