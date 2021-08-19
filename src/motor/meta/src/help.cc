/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.script.hh>
#include <motor/meta/engine/methodinfo.script.hh>
#include <motor/meta/engine/propertyinfo.script.hh>
#include <motor/meta/tags/documentation.script.hh>
#include <motor/meta/value.hh>
#include <zlib.h>

namespace Motor {

void help(const Meta::Type& type)
{
    motor_forceuse(type);
}

void help(const Meta::Class& klass)
{
    motor_info("%s" | klass.name);
    motor_forceuse(klass);
}

void help(const Meta::Property& property)
{
    motor_info("%s" | property.name);
    motor_forceuse(property);
}

void help(const Meta::Method& method)
{
    motor_info("%s" | method.name);
    motor_forceuse(method);
}

void help(const Meta::Method::Overload& overload)
{
    motor_forceuse(overload);
}

void help(const Meta::Method::Parameter& parameter)
{
    motor_info("%s" | parameter.name);
    motor_forceuse(parameter);
}

void help(const Meta::Value& v)
{
    motor_forceuse(v);
}

}  // namespace Motor
