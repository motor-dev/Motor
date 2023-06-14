/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_FEATURES_HH
#define MOTOR_MINITL_FEATURES_HH

#define MOTOR_OPTIM_LEVEL_DEBUG   1
#define MOTOR_OPTIM_LEVEL_PROFILE 2
#define MOTOR_OPTIM_LEVEL_FINAL   3

#ifdef MOTOR_DEBUG
#    define MOTOR_FLAVOUR     Debug
#    define MOTOR_OPTIM_LEVEL MOTOR_OPTIM_LEVEL_DEBUG
#elif defined(MOTOR_PROFILE)
#    define MOTOR_FLAVOUR     Profile
#    define MOTOR_OPTIM_LEVEL MOTOR_OPTIM_LEVEL_PROFILE
#else
#    define MOTOR_FLAVOUR     Final
#    define MOTOR_OPTIM_LEVEL MOTOR_OPTIM_LEVEL_FINAL
#endif

#define MOTOR_OPTIM_LEVEL_AT_MOST(x)  (MOTOR_OPTIM_LEVEL <= (x))
#define MOTOR_OPTIM_LEVEL_AT_LEAST(x) (MOTOR_OPTIM_LEVEL >= (x))

#if MOTOR_OPTIM_LEVEL_AT_MOST(MOTOR_OPTIM_LEVEL_DEBUG)
#    define MOTOR_ENABLE_ASSERT              1
#    define MOTOR_ENABLE_WEAKCHECK           1
#    define MOTOR_ENABLE_DEBUG_ITERATORS     1
#    define MOTOR_ENABLE_LOGGING             1
#    define MOTOR_ENABLE_MEMORY_TRACKING     1
#    define MOTOR_ENABLE_MEMORY_DEBUGGING    1
#    define MOTOR_ENABLE_EXCEPTIONS          MOTOR_SUPPORTS_EXCEPTIONS
#    define MOTOR_ENABLE_COMPONENT_DEBUGGING 1
#else
#    define MOTOR_ENABLE_ASSERT              0
#    define MOTOR_ENABLE_WEAKCHECK           0
#    define MOTOR_ENABLE_DEBUG_ITERATORS     0
#    define MOTOR_ENABLE_LOGGING             0
#    define MOTOR_ENABLE_MEMORY_TRACKING     0
#    define MOTOR_ENABLE_MEMORY_DEBUGGING    0
#    define MOTOR_ENABLE_EXCEPTIONS          0
#    define MOTOR_ENABLE_COMPONENT_DEBUGGING 0
#endif

#endif
