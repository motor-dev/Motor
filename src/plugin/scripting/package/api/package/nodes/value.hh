/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_PACKAGE_NODES_VALUE_HH_
#define BE_PACKAGE_NODES_VALUE_HH_
/**************************************************************************************************/

namespace BugEngine
{
class File;
class Folder;
}

namespace BugEngine { namespace PackageBuilder { namespace Nodes
{

class Value : public minitl::refcountable
{
protected:
    Value();
public:
    ~Value();

    virtual bool        isCompatible(const RTTI::Type& type) const = 0;
    virtual RTTI::Value as(const RTTI::Type& type) const = 0;
};


class Reference;

class ReferenceValue : public Value
{
private:
    ref<const Reference> m_value;
public:
    ReferenceValue(ref<const Reference> value);
    ~ReferenceValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};

class BoolValue : public Value
{
private:
    bool m_value;
public:
    BoolValue(bool value);
    ~BoolValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class IntValue : public Value
{
private:
    i64 m_value;
public:
    IntValue(i64 param);
    ~IntValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class Int2Value : public Value
{
private:
    bigint2 m_value;
public:
    Int2Value(i64 x, i64 y);
    ~Int2Value();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class Int3Value : public Value
{
private:
    bigint3 m_value;
public:
    Int3Value(i64 x, i64 y, i64 z);
    ~Int3Value();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class Int4Value : public Value
{
private:
    bigint4 m_value;
public:
    Int4Value(i64 x, i64 y, i64 z, i64 w);
    ~Int4Value();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class FloatValue : public Value
{
private:
    double m_value;
public:
    FloatValue(double value);
    ~FloatValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class Float2Value : public Value
{
private:
    float2 m_value;
public:
    Float2Value(double x, double y);
    ~Float2Value();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class Float3Value : public Value
{
private:
    float3 m_value;
public:
    Float3Value(double x, double y, double z);
    ~Float3Value();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class Float4Value : public Value
{
private:
    float4 m_value;
public:
    Float4Value(double x, double y, double z, double w);
    ~Float4Value();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class StringValue : public Value
{
private:
    const char* m_value;
public:
    StringValue(const char* value);
    ~StringValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class FileValue : public Value
{
private:
    weak<const File> m_value;
public:
    FileValue(weak<Folder> folder, const char* value);
    ~FileValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


class ArrayValue : public Value
{
private:
    minitl::vector< ref<Value> >    m_values;
public:
    ArrayValue(const minitl::vector< ref<Value> >& values);
    ~ArrayValue();

    virtual bool        isCompatible(const RTTI::Type& type) const override;
    virtual RTTI::Value as(const RTTI::Type& type) const override;
};


}}}

/**************************************************************************************************/
#endif
