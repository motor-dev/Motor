/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/array.hh>

#include <motor/introspect/dbcontext.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/minitl/array.hh>

namespace Motor { namespace Meta { namespace AST {

static const istring value_type = istring("value_type");

Array::Array(const minitl::vector< ref< Node > >& value) : Node(), m_value(value)
{
}

Array::~Array()
{
}

ConversionCost Array::distance(const Type& type) const
{
    if(type.metaclass->type() == Meta::ClassType_Array)
    {
        ConversionCost                  result = ConversionCost();
        raw< const ArrayOperatorTable > api    = type.metaclass->operators->arrayOperators;
        for(minitl::vector< ref< Node > >::const_iterator it = m_value.begin(); it != m_value.end();
            ++it)
        {
            ConversionCost itemCost = (*it)->distance(api->value_type);
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
    for(u32 i = 0; i < m_value.size(); ++i)
    {
        result = result & m_value[i]->resolve(context);
    }
    return result;
}

void Array::doEval(const Meta::Type& expectedType, Value& result) const
{
    Meta::Type valueType = expectedType.metaclass->operators->arrayOperators->value_type;

    minitl::array< Meta::Value > v(Arena::temporary(),
                                   motor_checked_numcast< u32 >(m_value.size()));
    for(u32 i = 0; i < m_value.size(); ++i)
    {
        m_value[i]->doEval(valueType, v[i]);
    }
    result = expectedType.metaclass->constructor->doCall(
        v.begin(), motor_checked_numcast< u32 >(m_value.size()));
}

void Array::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
