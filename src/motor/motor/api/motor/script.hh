/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MOTOR_SCRIPT_HH
#define MOTOR_MOTOR_SCRIPT_HH

#include <motor/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/resource/description.hh>

namespace Motor {

template < typename T >
class ScriptEngine;

template < typename T >
class Script : public Resource::Description< T >
{
    template < typename X >
    friend class ScriptEngine;

private:
    weak< const File > m_file;

protected:
    explicit Script(const weak< const File >& file) : m_file(file)
    {
    }
    ~Script() = default;

public:
    ifilename getScriptName() const
    {
        return m_file->getFileName();
    }
};

}  // namespace Motor

#include <motor/script.factory.hh>

#endif
