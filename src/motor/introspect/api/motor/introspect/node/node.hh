/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_NODE_HH
#define MOTOR_INTROSPECT_NODE_NODE_HH

#include <motor/introspect/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta { namespace AST {

class Array;
class Bool;
class FileName;
class Float;
class Integer;
class Object;
class Parameter;
class Property;
class Reference;
class String;

struct DbContext;

class motor_api(INTROSPECT) Node : public minitl::refcountable
{
    friend class Array;

public:
    struct Visitor;

private:
    enum State
    {
        Parsed,
        InResolution,
        ResolvedError,
        Resolved,
        Evaluated
    };
    minitl::vector< minitl::tuple< const istring, Meta::Value > > m_metadata;
    mutable Value                                                 m_cache;
    mutable State                                                 m_state;

protected:
    Node() : m_metadata(Arena::meta()), m_cache(), m_state(Parsed)
    {
    }
    virtual void doEval(const Type& expectedType, Value& result) const = 0;
    virtual bool doResolve(DbContext & context);
    virtual void doVisit(Node::Visitor & visitor) const = 0;

public:
    struct motor_api(INTROSPECT) Visitor
    {
        virtual ~Visitor() = default;
        virtual void accept(const weak< const Array >&                  arrayNode,
                            const minitl::vector< weak< const Node > >& arrayValue);
        virtual void accept(const weak< const Bool >& boolValue);
        virtual void accept(const weak< const FileName >& filenameValue);
        virtual void accept(const weak< const Float >& floatValue);
        virtual void accept(const weak< const Integer >& integerValue);
        virtual void accept(const weak< const Object >& objectValue);
        virtual void accept(const weak< const Parameter >& parameter, istring name,
                            const weak< const Node >& value);
        virtual void accept(const weak< const Property >& propertyValue);
        virtual void accept(const weak< const Reference >& referenceValue,
                            const Value&                   referencedValue);
        virtual void accept(const weak< const Reference >& referenceValue,
                            const weak< const Node >&      referencedNode);
        virtual void accept(const weak< const String >& stringValue);
    };

    virtual ConversionCost distance(const Type& type) const = 0;
    virtual ref< Node >    getProperty(DbContext & context, const inamespace& name) const;
    virtual raw< const Meta::Method > getCall(DbContext & context) const;
    bool                              resolve(DbContext & context);
    void                              eval(const Type& expectedType, Value& result) const;
    Value                             eval(const Type& expectedType) const;

    template < typename T >
    void setMetadata(const istring name, T value)
    {
        for(auto& it: m_metadata)
        {
            if(it.first == name)
            {
                it.second = value;
                return;
            }
        }
        m_metadata.emplace_back(name, Meta::Value());
        m_metadata.rbegin()->second = value;
    }
    const Value& getMetadata(istring name) const;

    void visit(Visitor & visitor) const;
};

}}}  // namespace Motor::Meta::AST

#endif
