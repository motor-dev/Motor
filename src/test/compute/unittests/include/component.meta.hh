/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/world/component/component.meta.hh>

namespace Motor { namespace Test { namespace Compute { namespace UnitTests {

struct ComponentFloat
{
    float value;
};

struct ComponentFloat2
{
    knl::float2 value;
};

struct ComponentFloat3
{
    knl::float3 value;
};

struct ComponentFloat4
{
    knl::float4 value;
};

struct ComponentFloat8
{
    knl::float8 value;
};

struct ComponentFloat16
{
    knl::float16 value;
};

struct ComponentInt
{
    int value;
};

struct ComponentInt2
{
    knl::int2 value;
};

struct ComponentInt3
{
    knl::int3 value;
};

struct ComponentInt4
{
    knl::int4 value;
};

struct ComponentInt8
{
    knl::int8 value;
};

struct ComponentInt16
{
    knl::int16 value;
};

struct ComponentDouble
{
    double value;
};

struct ComponentDouble2
{
    knl::double2 value;
};

struct ComponentDouble3
{
    knl::double3 value;
};

struct ComponentDouble4
{
    knl::double4 value;
};

struct ComponentDouble8
{
    knl::double8 value;
};

struct ComponentDouble16
{
    knl::double16 value;
};

}}}}  // namespace Motor::Test::Compute::UnitTests
