/* Motor <motor.devel@gmail.com>
  see LICENSE for detail */
#ifndef MOTOR_META_VALUE_HH
#define MOTOR_META_VALUE_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/type.meta.hh>

namespace Motor { namespace Meta {

class Class;
class Property;

class motor_api(META) Value
{
    friend class Class;
    friend class Property;

private:
    Type m_type;
    struct Reference
    {
        void* m_pointer;
        bool  m_deallocate;
    };
    union
    {
        Reference m_ref;
        char      m_data[47];
    } m_buffer;
    bool m_reference;

private:
    inline const void* memory() const;
    inline const void* rawget() const;
    inline void*       rawget();

private:
    template < typename T >
    struct ByRefType
    {
        T& value;
        explicit ByRefType(T& t) : value(t)
        {
        }
    };
    void* unpackAs(const Type& ti, ref< minitl::pointer >& rptr, weak< minitl::pointer >& wptr,
                   minitl::pointer*& obj);
    void  store(const void* src);

public:
    enum ReserveType
    {
        Reserve
    };

    Value(Type type, ReserveType);
    inline void* memory();

public:
    enum MakeCopyType
    {
        MakeCopy
    };

    inline Value();
    template < typename T >
    explicit Value(T t);
    Value(const Value& other);
    template < typename T >
    explicit Value(ByRefType< T > t);
    Value(Type typeinfo, void* location);
    Value(Type typeinfo, const void* location, MakeCopyType);
    Value(Type typeinfo, const Value& castFrom);
    ~Value();

    template < typename T >
    Value& operator=(const T& t);
    Value& operator=(const Value& other);

    inline Type type();
    inline Type type() const;

    template < typename T >
    inline const T as() const;
    template < typename T >
    inline T as();

    template < typename T >
    static inline ByRefType< T > ByRef(T& t)
    {
        return ByRefType< T >(t);
    }
    static inline ByRefType< const Value > ByRef(const Value& t)
    {
        return ByRefType< const Value >(t);
    }
    inline bool isConst() const;

    inline      operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool operator!() const;

    Value operator[](const istring& name);
    Value operator[](const istring& name) const;
    Value operator()(Value params[], u32 paramCount);

    void swap(Value& other) noexcept;

    inline bool isA(const Type& type) const
    {
        return m_type.isA(type);
    }
};

}}  // namespace Motor::Meta

#include <motor/meta/inl/value.hh>

#endif
