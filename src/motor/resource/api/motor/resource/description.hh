/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/resource/stdafx.h>

#include <motor/resource/idescription.meta.hh>

namespace Motor { namespace Resource {

template < typename T >
class Description : public IDescription
{
protected:
    Description()           = default;
    ~Description() override = default;
};

}}  // namespace Motor::Resource

#include <motor/resource/description.factory.hh>
