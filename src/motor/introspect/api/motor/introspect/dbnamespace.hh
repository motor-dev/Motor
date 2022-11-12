/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Namespace : public minitl::refcountable
{
private:
    minitl::Allocator&                           m_allocator;
    minitl::hashmap< istring, ref< Namespace > > m_children;
    minitl::hashmap< istring, ref< Node > >      m_nodes;
    Value                                        m_value;

public:
    Namespace(minitl::Allocator & allocator);
    Namespace(minitl::Allocator & allocator, const Value& value);
    ~Namespace();

    void             add(const inamespace& name, const Value& value);
    void             add(const inamespace& name, ref< Namespace > ns);
    void             add(const inamespace& name, ref< Node > node);
    void             remove(const inamespace& name, ref< Node > node);
    ref< Namespace > getChild(const istring name) const;
    ref< Node >      getNode(const istring name) const;
    const Value&     getValue() const;
};

}}}  // namespace Motor::Meta::AST
