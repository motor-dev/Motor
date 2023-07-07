/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/array.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/operatortable.hh>
#include <motor/minitl/utility.hh>
#include <motor/minitl/vector.hh>

namespace Motor { namespace Meta { namespace AST {

Array::Array(minitl::vector< ref< Node > > value) : Node(), m_value(minitl::move(value))
{
}

Array::~Array() = default;

ConversionCost Array::distance(const Type& type) const
{
    if(type.metaclass->operators->arrayOperators)
    {
        ConversionCost result    = ConversionCost();
        Type           valueType = type.metaclass->operators->arrayOperators->valueType;
        for(const auto& it: m_value)
        {
            ConversionCost itemCost = it->distance(valueType);
            if(itemCost > result) result = itemCost;
        }
        return result;
    }
    else
    {
        return Meta::ConversionCost::s_incompatible;
    }
}

bool Array::doResolve(DbContext& context)
{
    bool result = true;
    for(const auto& i: m_value)
    {
        result = result & i->resolve(context);
    }
    return result;
}

void Array::doEval(const Meta::Type& expectedType, Value& result) const
{
    Meta::Type valueType = expectedType.metaclass->operators->arrayOperators->valueType;

    minitl::vector< Meta::Value > v(Arena::temporary(),
                                    motor_checked_numcast< u32 >(m_value.size()));
    for(u32 i = 0; i < m_value.size(); ++i)
    {
        m_value[i]->doEval(valueType, v[i]);
    }
    result = expectedType.metaclass->constructor->doCall(
        v.data(), motor_checked_numcast< u32 >(m_value.size()));
}

void Array::doVisit(Node::Visitor& visitor) const
{
    minitl::vector< weak< const Node > > value(Arena::temporary(), m_value.begin(), m_value.end());
    visitor.accept(this, value);
}

}}}  // namespace Motor::Meta::AST
