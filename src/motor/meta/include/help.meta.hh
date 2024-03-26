/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_BUILTIN_HELP_META_HH
#define MOTOR_META_BUILTIN_HELP_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/property.meta.hh>

namespace Motor {

void help(const Meta::Type& type);
void help(const Meta::Class& klass);
void help(const Meta::Property& property);
void help(const Meta::Method& method);
void help(const Meta::Method::Overload& overload);
void help(const Meta::Method::Parameter& parameter);
void help(const Meta::Value& v);

}  // namespace Motor

#include <help.meta.factory.hh>

#endif
