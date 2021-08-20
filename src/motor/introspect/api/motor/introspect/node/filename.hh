/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INTROSPECT_NODE_FILENAME_HH_
#define MOTOR_INTROSPECT_NODE_FILENAME_HH_
/**************************************************************************************************/
#include <motor/introspect/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/introspect/node/node.hh>

namespace Motor { namespace Meta { namespace AST {

class motor_api(INTROSPECT) FileName : public Node
{
private:
    const ifilename m_value;
    weak< File >    m_file;

protected:
    virtual ConversionCost distance(const Type& type) const override;
    virtual bool           doResolve(DbContext & context) override;
    virtual void           doEval(const Type& expectedType, Value& result) const override;
    virtual void           doVisit(Node::Visitor & visitor) const override;

public:
    FileName(const ifilename& value);
    ~FileName();
};

}}}  // namespace Motor::Meta::AST

/**************************************************************************************************/
#endif
