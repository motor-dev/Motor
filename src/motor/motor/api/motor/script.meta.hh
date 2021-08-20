/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MOTOR_SCRIPT_SCRIPT_HH_
#define MOTOR_MOTOR_SCRIPT_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/resource/description.meta.hh>

namespace Motor {

template < typename T >
class ScriptEngine;
class motor_api(MOTOR) Script : public Resource::Description
{
    template < typename T >
    friend class ScriptEngine;

private:
    weak< const File > m_file;

protected:
    Script(weak< const File > file);
    ~Script();

public:
    ifilename getScriptName() const;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
