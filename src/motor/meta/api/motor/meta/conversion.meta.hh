/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_CONVERSION_META_HH_
#define MOTOR_META_CONVERSION_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>

namespace Motor { namespace Meta {

struct Type;

struct motor_api(META) ConversionCost
{
public:
    u8  incompatible;
    u8  variant;
    u16 conversion;
    u16 promotion;
    u16 qualification;

    ConversionCost(u16 qualification = 0, u16 promotion = 0, u16 conversion = 0, u8 variant = 0,
                   u8 incompatible = 0)
        : incompatible(incompatible)
        , variant(variant)
        , conversion(conversion)
        , promotion(promotion)
        , qualification(qualification)
    {
    }

    u64 value() const
    {
        return (u64(qualification)) | (u64(promotion) << 16) | (u64(conversion) << 32)
               | (u64(variant) << 48) | (u64(incompatible) << 56);
    }

    bool operator==(ConversionCost other) const
    {
        return value() == other.value();
    }
    bool operator!=(ConversionCost other) const
    {
        return value() != other.value();
    }
    bool operator<(ConversionCost other) const
    {
        return value() < other.value();
    }
    bool operator<=(ConversionCost other) const
    {
        return value() <= other.value();
    }
    bool operator>(ConversionCost other) const
    {
        return value() > other.value();
    }
    bool operator>=(ConversionCost other) const
    {
        return value() >= other.value();
    }
    ConversionCost operator+=(ConversionCost other)
    {
        incompatible  = motor_checked_numcast< u8 >(incompatible + other.incompatible);
        variant       = motor_checked_numcast< u8 >(incompatible + other.variant);
        conversion    = motor_checked_numcast< u16 >(conversion + other.conversion);
        promotion     = motor_checked_numcast< u16 >(promotion + other.promotion);
        qualification = motor_checked_numcast< u16 >(qualification + other.qualification);
        return *this;
    }

    static const ConversionCost s_incompatible;
    static const ConversionCost s_variant;
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
