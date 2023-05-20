/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>
#include <motor/scheduler/kernel/parameters/parametertype.hh>

#include <motor/scheduler/kernel/product.hh>

namespace Motor { namespace KernelScheduler {

template < typename T >
class Image1D : public IImage1D
{
private:
    MOTOR_EXPORT static IImage1D::ParameterRegistration s_registration;

public:
    Image1D()
    {
        motor_forceuse(s_registration);
    }
    ~Image1D() override = default;
};

template < typename T >
IImage1D::ParameterRegistration Image1D< T >::s_registration(motor_class< T >(),
                                                             motor_class< Image1D< T > >());

}}  // namespace Motor::KernelScheduler

#include <motor/scheduler/kernel/parameters/image1d.factory.hh>
