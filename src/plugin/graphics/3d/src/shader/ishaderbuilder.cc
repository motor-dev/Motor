/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/shader/ishaderbuilder.hh>

namespace Motor { namespace Shaders {

IShaderBuilder::Namespace::Namespace() : names(Arena::temporary())
{
}

IShaderBuilder::IShaderBuilder()
    : m_namespaces(Arena::temporary())
    , m_currentAttribute(0)
    , m_currentVarying(0)
    , m_currentAttributeToVarying(0)
    , m_currentTemporary(0)
    , m_attributeToVarying(Arena::temporary())
    , m_stream(Arena::temporary(), 10000)
    , m_indent(0)
{
    m_namespaces.emplace_back();
    m_stream.write("\0", 1);
}

IShaderBuilder::~IShaderBuilder() = default;

void IShaderBuilder::indent()
{
    m_indent++;
}

void IShaderBuilder::unindent()
{
    m_indent--;
}

void IShaderBuilder::write(const char* text)
{
    m_stream.erase(1);
    size_t size = text ? strlen(text) : 0;
    if(size)
    {
        for(int i = 0; i < m_indent; ++i)
            m_stream.write("  ", 2);
        m_stream.write(text, motor_checked_numcast< u32 >(strlen(text)));
    }
    m_stream.write("\0", 1);
}

void IShaderBuilder::writeln(const char* text)
{
    write(text);
    m_stream.write("\n\0", 2);
}

const char* IShaderBuilder::text() const
{
    return reinterpret_cast< const char* >(m_stream.memory());
}

i64 IShaderBuilder::textSize() const
{
    return m_stream.size();
}

istring IShaderBuilder::referenceNode(const weak< const Node >& node)
{
    for(minitl::vector< Namespace >::const_reverse_iterator it = m_namespaces.rbegin();
        it != m_namespaces.rend(); ++it)
    {
        minitl::hashmap< weak< const Node >, istring >::const_iterator name = it->names.find(node);
        if(name != it->names.end())
        {
            return name->second;
        }
    }
    motor_error(Log::shader(), "Undeclared object");
    return {};
}

void IShaderBuilder::addUniform(const weak< const Node >& node, Stage stage, const istring& name,
                                ValueType type)
{
    if(m_namespaces.front().names.insert(node, name).second)
    {
        doAddUniformDeclaration(name, stage, type);
    }
}

void IShaderBuilder::addVarying(const weak< const Node >& node, Stage currentStage,
                                Stage targetStage, ValueType type)
{
    if(currentStage == targetStage)
    {
        istring name(minitl::format< 1024u >(FMT("b_varying{0}"), m_currentVarying));
        if(m_namespaces.front().names.insert(node, name).second)
        {
            m_currentVarying++;
            doAddVaryingDeclaration(name, currentStage, type);
        }
    }
}

void IShaderBuilder::addAttribute(const weak< const Node >& node, Stage currentStage,
                                  Stage targetStage, ValueType type)
{
    if(VertexStage == targetStage)
    {
        istring nameAttribute(minitl::format< 1024u >(FMT("b_attribute{0}"), m_currentAttribute));
        istring nameVarying(
            minitl::format< 1024u >(FMT("b_attributeToVarying{0}"), m_currentAttributeToVarying));
        if(m_namespaces.front().names.insert(node, nameAttribute).second)
        {
            m_currentAttribute++;
            if(currentStage == VertexStage)
            {
                doAddAttributeDeclaration(nameAttribute, targetStage, type);
            }
            else
            {
                m_currentAttributeToVarying++;
                doAddAttributeDeclaration(nameAttribute, targetStage, type);
                doAddVaryingDeclaration(nameVarying, targetStage, type);
                m_attributeToVarying.push_back(minitl::make_tuple(nameAttribute, nameVarying));
            }
        }
    }
    else if(currentStage == targetStage)
    {
        istring nameVarying(
            minitl::format< 1024u >(FMT("b_attributeToVarying{0}"), m_currentAttributeToVarying));
        if(m_namespaces.front().names.insert(node, nameVarying).second)
        {
            m_currentAttributeToVarying++;
            doAddVaryingDeclaration(nameVarying, targetStage, type);
        }
    }
}

void IShaderBuilder::forwardAttributes()
{
    for(minitl::vector< minitl::tuple< istring, istring > >::const_iterator it
        = m_attributeToVarying.begin();
        it != m_attributeToVarying.end(); ++it)
    {
        doSaveTo(it->second, it->first);
    }
}

void IShaderBuilder::beginMethodDefinition(const istring& name)
{
    m_namespaces.emplace_back();
    doAddMethod(name);
}

void IShaderBuilder::end()
{
    m_namespaces.erase(m_namespaces.end() - 1);
    doEndMethod();
}

void IShaderBuilder::saveTo(Semantic semantic, const weak< const Node >& node)
{
    doSaveTo(semantic, referenceNode(node));
}

void IShaderBuilder::addOperator(const weak< const Node >& node, Operator op, ValueType type,
                                 const weak< const Node >& node1, const weak< const Node >& node2)
{
    istring var(minitl::format< 1024u >(FMT("temp_{0}"), m_currentTemporary));
    if(m_namespaces.front().names.insert(node, var).second)
    {
        m_currentTemporary++;
        const istring& op1 = referenceNode(node1);
        const istring& op2 = referenceNode(node2);
        doAddOperator(op, type, var, op1, op2);
    }
}

void IShaderBuilder::write(float value)
{
    doWrite(value);
}

void IShaderBuilder::write(knl::float2 value)
{
    doWrite(value);
}

void IShaderBuilder::write(knl::float3 value)
{
    doWrite(value);
}

void IShaderBuilder::write(knl::float4 value)
{
    doWrite(value);
}

void IShaderBuilder::write(int value)
{
    doWrite(value);
}

void IShaderBuilder::write(knl::int2 value)
{
    doWrite(value);
}

void IShaderBuilder::write(knl::int3 value)
{
    doWrite(value);
}

void IShaderBuilder::write(knl::int4 value)
{
    doWrite(value);
}

void IShaderBuilder::write(bool value)
{
    doWrite(value);
}

}}  // namespace Motor::Shaders
