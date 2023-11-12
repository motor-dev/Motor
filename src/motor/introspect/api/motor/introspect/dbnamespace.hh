/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_DBNAMESPACE_HH
#define MOTOR_INTROSPECT_DBNAMESPACE_HH

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) Namespace : public minitl::pointer
{
private:
    minitl::allocator&                           m_allocator;
    minitl::hashmap< istring, ref< Namespace > > m_children;
    minitl::hashmap< istring, ref< Node > >      m_nodes;
    Value                                        m_value;

public:
    explicit Namespace(minitl::allocator & allocator);
    Namespace(minitl::allocator & allocator, const Value& value);
    ~Namespace() override;

    void             add(const inamespace& name, const Value& value);
    void             add(const inamespace& name, const ref< Namespace >& ns);
    void             add(const inamespace& name, const ref< Node >& node);
    void             remove(const inamespace& name, const ref< Node >& node);
    ref< Namespace > getChild(istring name) const;
    ref< Node >      getNode(istring name) const;
    const Value&     getValue() const;
};

}}}  // namespace Motor::Meta::AST

#endif
