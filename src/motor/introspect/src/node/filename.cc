/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/node/filename.hh>

#include <motor/filesystem/file.meta.hh>
#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

FileName::FileName(const ifilename& value) : Node(), m_value(value), m_file()
{
    motor_forceuse(m_value);
}

FileName::~FileName() = default;

ConversionCost FileName::distance(const Type& type) const
{
    return motor_type< weak< const File > >().calculateConversion(type);
}

bool FileName::doResolve(DbContext& context)
{
    m_file = context.rootFolder->openFile(m_value);
    if(!m_file)
    {
        context.error(
            this, minitl::format< 512 >(FMT("could not open file: {0}: no such file or directory"),
                                        m_value));
        return false;
    }
    return true;
}

void FileName::doEval(const Type& expectedType, Value& result) const
{
    motor_forceuse(expectedType);
    result = Meta::Value(m_file);
}

void FileName::doVisit(Node::Visitor& visitor) const
{
    visitor.accept(this);
}

}}}  // namespace Motor::Meta::AST
