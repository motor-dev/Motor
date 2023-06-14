/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_NODE_FILENAME_HH
#define MOTOR_INTROSPECT_NODE_FILENAME_HH

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
    ConversionCost distance(const Type& type) const override;
    bool           doResolve(DbContext & context) override;
    void           doEval(const Type& expectedType, Value& result) const override;
    void           doVisit(Node::Visitor & visitor) const override;

public:
    explicit FileName(const ifilename& value);
    ~FileName() override;
};

}}}  // namespace Motor::Meta::AST

#endif
