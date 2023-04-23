/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>

#include <motor/core/threads/thread.hh>
#include <motor/plugin/dynobjectlist.hh>

#include <android/log.h>
#include <jni.h>

MOTOR_EXPORT const char* s_packagePath   = nullptr;
MOTOR_EXPORT const char* s_dataDirectory = nullptr;
MOTOR_EXPORT const char* s_plugin        = nullptr;

int beMain(int argc, const char* argv[]);

namespace Motor { namespace Android {

class AndroidLogListener : public Motor::ILogListener
{
public:
    AndroidLogListener() = default;

    ~AndroidLogListener() override = default;

protected:
    bool log(const Motor::inamespace& logname, Motor::LogLevel level, const char* filename,
             int line, const char* thread, const char* msg) const override
    {
        android_LogPriority s_motorToAndroid[logFatal + 1]
            = {ANDROID_LOG_DEBUG, ANDROID_LOG_INFO, ANDROID_LOG_WARN, ANDROID_LOG_ERROR,
               ANDROID_LOG_FATAL};
        android_LogPriority p = s_motorToAndroid[int(level)];
        __android_log_print(p, "Motor", "%s|%d: [%s:%s] %s", filename, line, thread,
                            logname.str().name, msg);
        return true;
    }
};

static intptr_t android_main(intptr_t /*width*/, intptr_t /*height*/)
{
    Motor::ScopedLogListener android_listener(
        scoped< AndroidLogListener >::create(Motor::Arena::debug()));
    Motor::Plugin::DynamicObjectList::showList();
    const char* args[] = {"Motor", s_plugin};
    return beMain(1 + (s_plugin != nullptr), args);
}

}}  // namespace Motor::Android

extern "C"
{
    JNIEXPORT void JNICALL Java_com_motor_MotorLib_setPaths(JNIEnv* env, jclass cls,
                                                            jstring packagePath,
                                                            jstring dataDirectory, jstring plugin);
    JNIEXPORT void JNICALL Java_com_motor_MotorLib_init(JNIEnv* env, jclass cls, jint width,
                                                        jint height);
    JNIEXPORT void JNICALL Java_com_motor_MotorLib_step(JNIEnv* env, jclass cls);
}

static Motor::Thread*  s_mainThread;
JNIEXPORT void JNICALL Java_com_motor_MotorLib_setPaths(JNIEnv* env, jclass /*cls*/,
                                                        jstring packagePath, jstring dataDirectory,
                                                        jstring plugin)
{
    s_packagePath   = env->GetStringUTFChars(packagePath, nullptr);
    s_dataDirectory = env->GetStringUTFChars(dataDirectory, nullptr);
    s_plugin        = env->GetStringUTFChars(plugin, nullptr);
}

JNIEXPORT void JNICALL Java_com_motor_MotorLib_init(JNIEnv* /*env*/, jclass /*cls*/, jint width,
                                                    jint height)
{
    s_mainThread = new Motor::Thread("android_main", &Motor::Android::android_main, width, height);
}

JNIEXPORT void JNICALL Java_com_motor_MotorLib_step(JNIEnv* /*env*/, jclass /*cls*/)
{
    motor_forceuse(s_mainThread);
}
