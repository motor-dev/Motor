/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/introspectionhint.meta.hh>
#include <motor/meta/engine/call.hh>

namespace Motor { namespace Meta { namespace AST {

static inline Meta::ConversionCost calculateConversion(weak< const Node > node,
                                                       const Meta::Type&  other)
{
    return node->distance(other);
}

static inline void convert(weak< const Node > node, void* buffer, Meta::Type type)
{
    new(buffer) Value(node->eval(type));
}

}}}  // namespace Motor::Meta::AST
