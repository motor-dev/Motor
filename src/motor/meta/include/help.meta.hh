/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>

namespace Motor {

void help(const Meta::Type& type);
void help(const Meta::Class& klass);
void help(const Meta::Property& property);
void help(const Meta::Method& method);
void help(const Meta::Method::Overload& overload);
void help(const Meta::Method::Parameter& parameter);
void help(const Meta::Value& v);

}  // namespace Motor
