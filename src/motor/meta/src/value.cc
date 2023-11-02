/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

#include <motor/meta/method.meta.hh>

namespace Motor { namespace Meta {

Value::Value(const Value& other) : m_type(other.m_type), m_buffer(), m_reference(other.m_reference)
{
    if(m_reference)
    {
        m_buffer.m_ref.m_pointer    = other.m_buffer.m_ref.m_pointer;
        m_buffer.m_ref.m_deallocate = false;
    }
    else
    {
        m_buffer.m_ref.m_pointer
            = m_type.size() > sizeof(m_buffer) ? Arena::script().alloc(m_type.size()) : nullptr;
        m_buffer.m_ref.m_deallocate = (m_buffer.m_ref.m_pointer != nullptr);
        m_type.copy(other.memory(), memory());
    }
}

Value::Value(Type type, const void* location, MakeCopyType)
    : m_type(type)
    , m_buffer()
    , m_reference(false)
{
    m_buffer.m_ref.m_pointer
        = m_type.size() > sizeof(m_buffer) ? Arena::script().alloc(m_type.size()) : nullptr;
    m_buffer.m_ref.m_deallocate = m_buffer.m_ref.m_pointer != nullptr;
    m_type.copy(location, memory());
}

Value::Value(Type type, void* location) : m_type(type), m_buffer(), m_reference(true)
{
    m_buffer.m_ref.m_pointer    = location;
    m_buffer.m_ref.m_deallocate = false;
}

Value::Value(Type typeinfo, const Value& castFrom)
    : m_type(typeinfo)
    , m_buffer()
    , m_reference(false)
{
    motor_assert_format(m_type.metaclass->isA(castFrom.type().metaclass)
                            || castFrom.type().metaclass->isA(m_type.metaclass),
                        "cannot cast from {0} to {1}", castFrom.type(), m_type);
    motor_assert_format(m_type.indirection != Type::Indirection::Value
                            || castFrom.type().isA(m_type),
                        "cannot upcast value type from {0} to {1}", castFrom.type(), m_type);

    m_buffer.m_ref.m_pointer
        = m_type.size() > sizeof(m_buffer) ? Arena::script().alloc(m_type.size()) : nullptr;
    m_buffer.m_ref.m_deallocate = (m_buffer.m_ref.m_pointer != nullptr);
    m_type.copy(castFrom.memory(), memory());
}

Value::Value(Type type, ReserveType) : m_type(type), m_buffer(), m_reference(false)
{
    m_buffer.m_ref.m_pointer
        = m_type.size() > sizeof(m_buffer) ? Arena::script().alloc(m_type.size()) : nullptr;
    m_buffer.m_ref.m_deallocate = m_buffer.m_ref.m_pointer != nullptr;
}

Value::~Value()
{
    if(!m_reference)
    {
        m_type.destroy(memory());
        if(m_type.size() > sizeof(m_buffer) && m_buffer.m_ref.m_deallocate)
        {
            Arena::script().free(m_buffer.m_ref.m_pointer);
        }
    }
}

Value& Value::operator=(const Value& other)
{
    if(m_reference)
    {
        if(motor_assert_format(m_type.isA(other.m_type),
                               "Value has type {0}; unable to copy from type {1}", m_type,
                               other.m_type))
            return *this;
        if(motor_assert(m_type.constness != Type::Constness::Const, "Value is const")) return *this;
        void* mem = memory();
        m_type.destroy(mem);
        m_type.copy(other.memory(), mem);
    }
    else
    {
        this->~Value();
        new((void*)this) Value(other);
    }
    return *this;
}

void* Value::unpackAs(const Type& ti, ref< minitl::refcountable >& rptr,
                      weak< minitl::refcountable >& wptr, minitl::refcountable*& obj)
{
    motor_assert_format(m_type.isA(ti), "Value has type {0}; unable to unbox to type {1}", m_type,
                        ti);
    void* mem = memory();
    switch(m_type.indirection)
    {
    case Type::Indirection::RefPtr:
        if(ti.indirection == Type::Indirection::RefPtr) break;
        rptr = *(ref< minitl::refcountable >*)mem;
        wptr = rptr;
        mem  = (void*)&wptr;
        /* falls through */
    case Type::Indirection::WeakPtr:
        if(ti.indirection == Type::Indirection::WeakPtr) break;
        wptr = *(weak< minitl::refcountable >*)mem;
        obj  = wptr.operator->();
        mem  = (void*)&obj;
        /* falls through */
    case Type::Indirection::RawPtr:
        if(ti.indirection == Type::Indirection::RawPtr) break;
        mem = *(void**)mem;
        /* falls through */
    default: break;
    }
    return mem;
}

void Value::store(const void* src)
{
    m_buffer.m_ref.m_pointer
        = m_type.size() > sizeof(m_buffer) ? Arena::script().alloc(m_type.size()) : nullptr;
    m_buffer.m_ref.m_deallocate = m_buffer.m_ref.m_pointer != nullptr;
    m_type.copy(src, memory());
}

Value Value::operator[](const istring& name)
{
    bool found;
    return m_type.metaclass->get(*this, name, found);
}

Value Value::operator[](const istring& name) const
{
    bool found;
    return m_type.metaclass->get(*this, name, found);
}

Value Value::operator()(Value params[], u32 paramCount)
{
    static const istring callName("?call");
    Value                call = (*this)[callName];
    if(motor_assert_format(call, "Not a callable object: {0}", m_type)) return {};
    if(motor_assert_format(call.isA(motor_type< const Method* const >()),
                           "Not a callable object: {0}", m_type))
        return {};
    return call.as< const Method* const >()->doCall(params, paramCount);
}

void Value::swap(Value& other)
{
    if(&other != this)
    {
        if(m_reference && other.m_reference)
        {
            minitl::swap(m_type, other.m_type);
            minitl::swap(m_buffer.m_ref, other.m_buffer.m_ref);
        }
        else if(m_reference)
        {
            minitl::swap(m_type, other.m_type);
            minitl::swap(m_reference, other.m_reference);
            Reference r = m_buffer.m_ref;
            m_type.copy(other.m_buffer.m_data, m_buffer.m_data);
            m_type.destroy(other.m_buffer.m_data);
            other.m_buffer.m_ref = r;
        }
        else if(other.m_reference)
        {
            Reference r = other.m_buffer.m_ref;
            m_type.copy(m_buffer.m_data, other.m_buffer.m_data);
            m_type.destroy(m_buffer.m_data);
            m_buffer.m_ref = r;
            minitl::swap(m_type, other.m_type);
            minitl::swap(m_reference, other.m_reference);
        }
        else
        {
            Value v(*this);
            *this = other;
            other = v;
        }
    }
}

}}  // namespace Motor::Meta
