/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>

namespace Motor {

void help(const Meta::Type& type)
{
    motor_forceuse(type);
}

void help(const Meta::Class& klass)
{
    motor_forceuse(klass);
}

void help(const Meta::Property& property)
{
    motor_forceuse(property);
}

void help(const Meta::Method& method)
{
    motor_forceuse(method);
}

void help(const Meta::Method::Overload& overload)
{
    motor_forceuse(overload);
}

void help(const Meta::Method::Parameter& parameter)
{
    motor_forceuse(parameter);
}

void help(const Meta::Value& v)
{
    motor_forceuse(v);
}

}  // namespace Motor
