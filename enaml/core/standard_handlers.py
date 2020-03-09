#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from types import FunctionType

from atom.api import Atom, Typed

from .dynamicscope import DynamicScope
from .expression_engine import ReadHandler, WriteHandler
from .funchelper import call_func
from .standard_inverter import StandardInverter
from .standard_tracer import StandardTracer


class HandlerMixin(Atom):
    """ A mixin class which provides common handler functionality.

    """
    #: The function to invoke to execute the expression. This value is
    #: provided by the standard operators, and will be appropriate for
    #: the given handler type.
    func = Typed(FunctionType)

    #: The key for the local scope in the storage map. This value is
    #: generated by the compiler and provided by the operators.
    scope_key = Typed(object)

    def get_locals(self, owner):
        """ Get a mapping of locals for expression evaluation.

        Parameters
        ----------
        owner : Declarative
            The object on which the handler is executing.

        Returns
        -------
        result : mapping
            A mapping object to use as the local scope.

        """
        return owner._d_storage.get(self.scope_key) or {}


class StandardReadHandler(ReadHandler, HandlerMixin):
    """ An expression read handler for simple read semantics.

    This handler is used in conjunction with the standard '=' operator.

    """
    def __call__(self, owner, name):
        """ Evaluate and return the expression value.

        """
        func = self.func
        f_globals = func.__globals__
        f_builtins = f_globals['__builtins__']
        f_locals = self.get_locals(owner)
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins)
        return call_func(func, (), {}, scope)


class StandardWriteHandler(WriteHandler, HandlerMixin):
    """ An expression write handler for simple write semantics.

    This handler is used in conjuction with the standard '::' operator.

    """
    def __call__(self, owner, name, change):
        """ Write the change to the expression.

        """
        func = self.func
        f_globals = func.__globals__
        f_builtins = f_globals['__builtins__']
        f_locals = self.get_locals(owner)
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins, change)
        call_func(func, (), {}, scope)


class StandardTracedReadHandler(ReadHandler, HandlerMixin):
    """ An expression read handler which traces code execution.

    This handler is used in conjuction with the standard '<<' operator.

    """
    def __call__(self, owner, name):
        """ Evaluate and return the expression value.

        """
        func = self.func
        f_globals = func.__globals__
        f_builtins = f_globals['__builtins__']
        f_locals = self.get_locals(owner)
        tr = StandardTracer(owner, name)
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins, None, tr)
        return call_func(func, (tr,), {}, scope)


class StandardInvertedWriteHandler(WriteHandler, HandlerMixin):
    """ An expression writer which writes an expression value.

    This handler is used in conjuction with the standard '>>' operator.

    """
    def __call__(self, owner, name, change):
        """ Write the change to the expression.

        """
        func = self.func
        f_globals = func.__globals__
        f_builtins = f_globals['__builtins__']
        f_locals = self.get_locals(owner)
        scope = DynamicScope(owner, f_locals, f_globals, f_builtins)
        inverter = StandardInverter(scope)
        call_func(func, (inverter, change['value']), {}, scope)
