/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/dbnamespace.hh>
#include <motor/introspect/node/object.hh>

namespace Motor { namespace Meta { namespace AST {

Namespace::Namespace(minitl::allocator& allocator)
    : m_allocator(allocator)
    , m_children(m_allocator)
    , m_nodes(m_allocator)
    , m_value()
{
}

Namespace::Namespace(minitl::allocator& allocator, const Value& value)
    : m_allocator(allocator)
    , m_children(m_allocator)
    , m_nodes(m_allocator)
    , m_value(value)
{
}

Namespace::~Namespace() = default;

void Namespace::add(const inamespace& name, const Value& value)
{
    weak< Namespace > current = this;
    for(u32 i = 0; i < name.size(); ++i)
    {
        istring                                                                       n = name[i];
        minitl::tuple< minitl::hashmap< istring, ref< Namespace > >::iterator, bool > result
            = current->m_children.insert(n, ref< Namespace >());
        if(result.second)
        {
            result.first->second
                = ref< Namespace >::create(current->m_allocator, byref(current->m_allocator));
        }
        current = result.first->second;
    }
    current->m_value = value;
}

void Namespace::add(const inamespace& name, const ref< Namespace >& ns)
{
    weak< Namespace > current = this;
    if(name.size())
    {
        for(u32 i = 0; i < name.size() - 1; ++i)
        {
            istring n = name[i];
            minitl::tuple< minitl::hashmap< istring, ref< Namespace > >::iterator, bool > result
                = current->m_children.insert(n, ref< Namespace >());
            if(result.second)
            {
                result.first->second
                    = ref< Namespace >::create(current->m_allocator, byref(current->m_allocator));
            }
        }
        current->m_children[name[name.size() - 1]] = ns;
    }
}

void Namespace::add(const inamespace& name, const ref< Node >& node)
{
    weak< Namespace > current = this;
    if(name.size())
    {
        for(u32 i = 0; i < name.size() - 1; ++i)
        {
            istring n = name[i];
            minitl::tuple< minitl::hashmap< istring, ref< Namespace > >::iterator, bool > result
                = current->m_children.insert(n, ref< Namespace >());
            if(result.second)
            {
                result.first->second
                    = ref< Namespace >::create(current->m_allocator, byref(current->m_allocator));
            }
        }
        current->m_nodes[name[name.size() - 1]] = node;
    }
}

void Namespace::remove(const inamespace& name, const ref< Node >& node)
{
    weak< Namespace > current = this;
    if(name.size())
    {
        for(u32 i = 0; i < name.size() - 1; ++i)
        {
            current = current->getChild(name[i]);
            if(motor_assert_format(
                   current, "could not remove object {0}: unable to find child namespace {1}", name,
                   name[i]))
                return;
        }
        motor_assert_format(node == current->m_nodes[name[name.size() - 1]],
                            "node {0} does not match the node to remove", name);
        current->m_nodes.erase(current->m_nodes.find(name[name.size() - 1]));
    }
}

ref< Namespace > Namespace::getChild(istring name) const
{
    minitl::hashmap< istring, ref< Namespace > >::const_iterator it = this->m_children.find(name);
    if(it != m_children.end())
    {
        return it->second;
    }
    else
    {
        return {};
    }
}

ref< Node > Namespace::getNode(istring name) const
{
    minitl::hashmap< istring, ref< Node > >::const_iterator it = this->m_nodes.find(name);
    if(it != m_nodes.end())
    {
        return it->second;
    }
    else
    {
        return ref< Object >();
    }
}

const Value& Namespace::getValue() const
{
    return m_value;
}

}}}  // namespace Motor::Meta::AST
