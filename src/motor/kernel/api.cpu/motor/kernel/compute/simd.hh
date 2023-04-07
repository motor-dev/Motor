/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/kernel/stdafx.h>

namespace knl {

template < typename T, unsigned C >
struct array;

template < typename T >
struct array< T, 2 >
{
    T _0;
    T _1;
};

template < typename T >
struct array< T, 3 >
{
    T _0;
    T _1;
    T _2;
};

template < typename T >
struct array< T, 4 >
{
    T _0;
    T _1;
    T _2;
    T _3;
};
template < typename T >
struct array< T, 8 >
{
    T _0;
    T _1;
    T _2;
    T _3;
    T _4;
    T _5;
    T _6;
    T _7;
};
template < typename T >
struct array< T, 16 >
{
    T _0;
    T _1;
    T _2;
    T _3;
    T _4;
    T _5;
    T _6;
    T _7;
    T _8;
    T _9;
    T _10;
    T _11;
    T _12;
    T _13;
    T _14;
    T _15;
};

typedef knl::array< u8, 4 >      color32;
typedef knl::array< float, 4 >   color128;
typedef knl::array< u8, 2 >      ubyte2;
typedef knl::array< u8, 3 >      ubyte3;
typedef knl::array< u8, 4 >      ubyte4;
typedef knl::array< u8, 8 >      ubyte8;
typedef knl::array< u8, 16 >     ubyte16;
typedef knl::array< i8, 2 >      byte2;
typedef knl::array< i8, 3 >      byte3;
typedef knl::array< i8, 4 >      byte4;
typedef knl::array< i8, 8 >      byte8;
typedef knl::array< i8, 16 >     byte16;
typedef knl::array< u16, 2 >     ushort2;
typedef knl::array< u16, 3 >     ushort3;
typedef knl::array< u16, 4 >     ushort4;
typedef knl::array< u16, 8 >     ushort8;
typedef knl::array< u16, 16 >    ushort16;
typedef knl::array< i16, 2 >     short2;
typedef knl::array< i16, 3 >     short3;
typedef knl::array< i16, 4 >     short4;
typedef knl::array< i16, 8 >     short8;
typedef knl::array< i16, 16 >    short16;
typedef knl::array< u32, 2 >     uint2;
typedef knl::array< u32, 3 >     uint3;
typedef knl::array< u32, 4 >     uint4;
typedef knl::array< u32, 8 >     uint8;
typedef knl::array< u32, 16 >    uint16;
typedef knl::array< i32, 2 >     int2;
typedef knl::array< i32, 3 >     int3;
typedef knl::array< i32, 4 >     int4;
typedef knl::array< i32, 8 >     int8;
typedef knl::array< i32, 16 >    int16;
typedef knl::array< u64, 2 >     biguint2;
typedef knl::array< u64, 3 >     biguint3;
typedef knl::array< u64, 4 >     biguint4;
typedef knl::array< u64, 8 >     biguint8;
typedef knl::array< u64, 16 >    biguint16;
typedef knl::array< i64, 2 >     bigint2;
typedef knl::array< i64, 3 >     bigint3;
typedef knl::array< i64, 4 >     bigint4;
typedef knl::array< i64, 8 >     bigint8;
typedef knl::array< i64, 16 >    bigint16;
typedef knl::array< float, 2 >   float2;
typedef knl::array< float, 3 >   float3;
typedef knl::array< float, 4 >   float4;
typedef knl::array< float, 8 >   float8;
typedef knl::array< float, 16 >  float16;
typedef knl::array< double, 2 >  double2;
typedef knl::array< double, 3 >  double3;
typedef knl::array< double, 4 >  double4;
typedef knl::array< double, 8 >  double8;
typedef knl::array< double, 16 > double16;

}  // namespace knl
